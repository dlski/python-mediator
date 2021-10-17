import inspect
from dataclasses import dataclass
from inspect import Parameter
from typing import Any, List, Optional, get_type_hints


@dataclass
class CallableArg:
    """
    Stores information about given callable argument.
    """

    # argument name
    name: str
    # argument type annotation
    type: Optional[Any]
    # argument is positional flag
    is_positional: bool


@dataclass
class CallableType:
    """
    Stores information about callable type.
    """

    # when True callable is a routine
    is_routine: bool
    # when True callable is a method
    is_method: bool
    # when True callable returns awaitable result
    is_async: bool


@dataclass
class CallableIODetails:
    """
    Stores all information about input arguments and output data type.
    """

    # list of callable arguments details
    args: List[CallableArg]
    # when True callable accepts variadic keyword args like **kwargs
    has_kwargs: bool
    # return type annotation
    return_type: Optional[Any]

    def arg_by_name(self, name: str) -> Optional[CallableArg]:
        """
        Returns callable argument details with matching name,
        or None when there is no match.
        :param name: argument name
        :return: callable argument details or None when not found
        """
        for arg in self.args:
            if arg.name == name:
                return arg
        return None


@dataclass
class CallableDetails(CallableType, CallableIODetails):
    """
    Stores all inspection data about callable.
    """

    # reference to inspected object
    obj: Any


class CallableInspector:
    """
    Raw callable object inspector. Provides raw callable details is structured form.
    """

    _kinds = (
        Parameter.POSITIONAL_ONLY,
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.KEYWORD_ONLY,
    )
    _positional_kinds = (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)

    @classmethod
    def inspect(cls, fn: Any) -> CallableDetails:
        """
        Inspects given callable object.
        :param fn: raw callable object to inspect
        :return: callable structured details
        """
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
        """
        Inspects and provides given callable type information.
        :param fn: raw callable to inspect
        :return: callable type structured information
        """
        is_routine = inspect.isroutine(fn)
        return CallableType(
            is_routine=is_routine,
            is_method=inspect.ismethod(fn),
            is_async=inspect.iscoroutinefunction(fn if is_routine else fn.__call__),
        )

    @classmethod
    def io_details(cls, fn: Any) -> CallableIODetails:
        """
        Inspects and provides given callable input and output details.
        :param fn: raw callable to inspect
        :return: callable input and output structured details
        """
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
