from typing import Any, Dict, Optional, Sequence, Tuple

from mediator.common.factory.base import (
    HandlerFactoryError,
    IncompatibleHandlerFactoryError,
)
from mediator.common.handler import CallableHandler, Handler
from mediator.utils.inspection import CallableArg, CallableDetails, CallableInspector


class CallableObjDetails:
    """
    Utility that wraps callable object inspection procedure into handler factory world.
    """

    def __call__(self, obj: Any) -> CallableDetails:
        """
        Provides callable object inspection result
        or raises an error when obj is not callable.
        :param obj: callable object to inspect
        :raises IncompatibleHandlerFactoryError: when obj is not valid callable
        :return: `CallableDetails` object
        """
        try:
            return CallableInspector.inspect(obj)
        except TypeError as e:
            raise IncompatibleHandlerFactoryError(f"{obj!r}: {e}")


class CallableAttributeDetails:
    """
    Utility that (optionally) checks if object has valid type
    and performs callable inspection for given object attribute.
    """

    name: str
    subtype_of: Tuple[Any, ...]

    def __init__(self, name: str, owner_subtype_of: Sequence[Any] = ()):
        """
        Initializes callable attribute inspection object,
        that (optionally) checks if object has valid type
        and performs callable inspection for given object attribute
        :param name: inspection object attribute name
        :param owner_subtype_of: sequence of types to check
        if an instance of an input object is one of them;
        just like `isinstance(obj, owner_subtype_of)`
        """
        self.name = name
        self.subtype_of = tuple(owner_subtype_of)

    def __call__(self, obj: Any) -> CallableDetails:
        """
        (Optionally) checks if object has valid type
        and performs callable inspection for given object attribute.
        :param obj: input object
        :raises IncompatibleHandlerFactoryError: when object type is not supported
        :raises IncompatibleHandlerFactoryError:
        when object has no attribute with expected name
        :raises IncompatibleHandlerFactoryError:
        when expected attribute is not callable
        :return: callable object attribute `CallableDetails` result
        """
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
    """
    Utility that finds primary argument for given callable object,
    to be filled with action subject (event, request, command etc object).
    """

    def __init__(self, name: Optional[str] = None):
        """
        Initializes utility that finds primary argument for given callable object.
        :param name: optional argument name hint;
        when provided utility will assume argument with that name as primary
        """
        self.name = name

    def __call__(self, details: CallableDetails) -> CallableArg:
        """
        Provides callable primary argument using `CallableDetails` object.
        :param details: callable details to use
        :raises IncompatibleHandlerFactoryError: when callable has no arguments
        :raises IncompatibleHandlerFactoryError: when argument name was specified,
        but no matching argument was found
        :raises IncompatibleHandlerFactoryError: when argument has no or invalid type
        :raises HandlerFactoryError:
        when for found primary argument cannot be determined unequivocal type
        :return: primary argument details
        """
        if not details.args:
            raise IncompatibleHandlerFactoryError(
                f"Callable {details.obj!r} has no explicit argument"
            )
        arg = self._find(details)
        self._check_type(details, arg)
        return arg

    def _find(self, details: CallableDetails) -> CallableArg:
        """
        Finds primary callable argument using given details
        :param details: callable details
        :raises IncompatibleHandlerFactoryError: when callable has no arguments
        :raises IncompatibleHandlerFactoryError: when argument name was specified,
        but no matching argument was found
        :return: primary argument details
        """
        if self.name:
            return self._find_by_name(details, self.name)
        else:
            return self._get_first(details)

    @staticmethod
    def _find_by_name(details: CallableDetails, name: str):
        """
        Tries to find primary argument by name using given callable details.
        :param details: callable details
        :param name: argument name
        :raises IncompatibleHandlerFactoryError: when no matching argument was found
        :return: primary argument details
        """
        arg = details.arg_by_name(name)
        if not arg:
            raise IncompatibleHandlerFactoryError(
                f"Callable {details.obj!r} has no argument named {name}"
            )
        return arg

    @staticmethod
    def _get_first(details: CallableDetails) -> CallableArg:
        """
        Returns first callable argument as primary
        :param details: callable details
        :return: primary argument details
        """
        return details.args[0]

    @staticmethod
    def _check_type(details: CallableDetails, arg: CallableArg):
        """
        Checks given primary argument candidate is a valid one
        :param details: callable details
        :param arg: primary argument candidate details
        :raises HandlerFactoryError:
        when for given primary argument cannot be determined unequivocal type
        """
        if arg.type is None:
            raise HandlerFactoryError(
                f"Callable {details.obj!r} argument {arg.name} has no type annotation"
            )
        if not isinstance(arg.type, type):
            raise HandlerFactoryError(
                f"Callable {details.obj!r} argument {arg.name}"
                f" type annotation is not a type"
            )


class CallableHandlerCreate:
    """
    Creates callable handler using given specification.
    """

    def __init__(
        self, subject_as_keyword: bool, arg_map: Dict[str, str], arg_strict: bool
    ):
        """
        Initializes callable handler factory using given specification.
        :param subject_as_keyword:
        force to provide primary (subject) argument as keyword argument
        :param arg_map: action extra arguments to callable arguments name mapping;
        used for translation to reconcile argument name differences
        :param arg_strict: when True all action arguments will be provided for handler,
        when False only those that fits into handler callable arguments set
        (excessive ones will be dropped)
        """
        self.subject_as_keyword = subject_as_keyword
        self.arg_map = arg_map
        self.arg_strict = arg_strict

    def __call__(self, details: CallableDetails, arg: CallableArg, obj: Any) -> Handler:
        """
        Creates callable handler using given specification and configuration.
        :param details: callable details
        :param arg: primary (subject) argument specification
        :param obj: underlying object
        - source of callable object and handler behaviour information object
        :raises HandlerFactoryError: when callable object is not async callable
        :return: handler object that can call underlying callable using provided action
        """
        if not details.is_async:
            raise HandlerFactoryError(f"Object {details.obj!r} is not async callable")

        subject_name: Optional[str]
        if self.subject_as_keyword or not arg.is_positional:
            subject_name = arg.name
        else:
            subject_name = None

        if self.arg_strict or details.has_kwargs:
            allow_args = None
        else:
            allow_args = {arg.name for arg in details.args}

        return CallableHandler(
            obj=obj,
            fn=details.obj,
            key=arg.type,
            subject_name=subject_name,
            arg_map=self.arg_map,
            allow_args=allow_args,
        )
