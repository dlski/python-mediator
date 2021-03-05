import inspect
from dataclasses import dataclass
from inspect import Parameter
from typing import Any, List, Optional, get_type_hints


@dataclass
class CallableArg:
    name: str
    type: Optional[Any]
    is_positional: bool


@dataclass
class CallableType:
    is_routine: bool
    is_method: bool
    is_async: bool


@dataclass
class CallableIODetails:
    args: List[CallableArg]
    has_kwargs: bool
    return_type: Optional[Any]

    def arg_by_name(self, name: str) -> Optional[CallableArg]:
        for arg in self.args:
            if arg.name == name:
                return arg
        return None


@dataclass
class CallableDetails(CallableType, CallableIODetails):
    obj: Any


class CallableInspector:
    _kinds = (
        Parameter.POSITIONAL_ONLY,
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.KEYWORD_ONLY,
    )
    _positional_kinds = (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)

    @classmethod
    def inspect(cls, fn: Any) -> CallableDetails:
        if not callable(fn):
            raise TypeError("Object is not callable")
        type_ = cls.callable_type(fn)
        io_details = cls.io_details(fn)
        return CallableDetails(
            args=io_details.args,
            has_kwargs=io_details.has_kwargs,
            return_type=io_details.return_type,
            is_routine=type_.is_routine,
            is_method=type_.is_method,
            is_async=type_.is_async,
            obj=fn,
        )

    @staticmethod
    def callable_type(fn: Any) -> CallableType:
        is_routine = inspect.isroutine(fn)
        return CallableType(
            is_routine=is_routine,
            is_method=inspect.ismethod(fn),
            is_async=inspect.iscoroutinefunction(fn if is_routine else fn.__call__),
        )

    @classmethod
    def io_details(cls, fn: Any) -> CallableIODetails:
        if not inspect.isroutine(fn):
            fn = fn.__call__
        signature = inspect.signature(fn)
        annotations = get_type_hints(fn)
        return CallableIODetails(
            args=[
                CallableArg(
                    name=param.name,
                    type=annotations.get(param.name),
                    is_positional=param.kind in cls._positional_kinds,
                )
                for param in signature.parameters.values()
                if param.kind in cls._kinds
            ],
            has_kwargs=any(
                param.kind == Parameter.VAR_KEYWORD
                for param in signature.parameters.values()
            ),
            return_type=annotations.get("return"),
        )
