from typing import Any, Dict, Optional, Sequence, Tuple

from mediator.common.factory.base import (
    HandlerFactoryError,
    IncompatibleHandlerFactoryError,
)
from mediator.common.handler import Handler, MappedDirectHandler
from mediator.utils.inspection import CallableArg, CallableDetails, CallableInspector


class CallableObjDetails:
    def __call__(self, obj: Any) -> CallableDetails:
        try:
            return CallableInspector.inspect(obj)
        except TypeError as e:
            raise IncompatibleHandlerFactoryError(f"{obj!r}: {e}")


class CallableAttributeDetails:
    name: str
    subtype_of: Tuple[Any, ...]

    def __init__(self, name: str, owner_subtype_of: Sequence[Any] = ()):
        self.name = name
        self.subtype_of = tuple(owner_subtype_of)

    def __call__(self, obj: Any) -> CallableDetails:
        if self.subtype_of:
            if not isinstance(obj, self.subtype_of):
                raise IncompatibleHandlerFactoryError(
                    f"Object {obj!r} is not type of {self.subtype_of}"
                )

        try:
            attr = getattr(obj, self.name)
        except AttributeError:
            raise IncompatibleHandlerFactoryError(
                f"Object {obj!r} has no attribute named {self.name}"
            )

        try:
            return CallableInspector.inspect(attr)
        except TypeError as e:
            raise IncompatibleHandlerFactoryError(f"{obj!r} attribute {self.name}: {e}")


class HandlerSubjectArgGet:
    def __init__(self, name: Optional[str] = None):
        self.name = name

    def __call__(self, details: CallableDetails) -> CallableArg:
        if not details.args:
            raise IncompatibleHandlerFactoryError(
                f"Callable {details.obj!r} has no explicit argument"
            )
        arg = self._find(details)
        self._check_type(details, arg)
        return arg

    def _find(self, details: CallableDetails) -> CallableArg:
        if self.name:
            return self._find_by_name(details, self.name)
        else:
            return self._get_first(details)

    @staticmethod
    def _find_by_name(details: CallableDetails, name: str):
        arg = details.arg_by_name(name)
        if not arg:
            raise IncompatibleHandlerFactoryError(
                f"Callable {details.obj!r} has no argument named {name}"
            )
        return arg

    @staticmethod
    def _get_first(details: CallableDetails):
        return details.args[0]

    @staticmethod
    def _check_type(details: CallableDetails, arg: CallableArg):
        if arg.type is None:
            raise HandlerFactoryError(
                f"Callable {details.obj!r} argument {arg.name} has no type annotation"
            )
        if not isinstance(arg.type, type):
            raise HandlerFactoryError(
                f"Callable {details.obj!r} argument {arg.name}"
                f" type annotation is not a type"
            )


class DirectHandlerCreate:
    def __init__(
        self, subject_as_keyword: bool, arg_map: Dict[str, str], arg_strict: bool
    ):
        self.subject_as_keyword = subject_as_keyword
        self.arg_map = arg_map
        self.arg_strict = arg_strict

    def __call__(self, details: CallableDetails, arg: CallableArg, obj: Any) -> Handler:
        if not details.is_async:
            raise HandlerFactoryError(f"Object {details.obj!r} is not async callable")
        if self.subject_as_keyword or not arg.is_positional:
            subject_name = arg.name
        else:
            subject_name = None
        if self.arg_strict or details.has_kwargs:
            arg_filter = None
        else:
            arg_filter = {arg.name for arg in details.args}
        return MappedDirectHandler(
            handler=obj,
            fn=details.obj,
            key=arg.type,
            subject_name=subject_name,
            arg_map=self.arg_map,
            arg_filter=arg_filter,
        )
