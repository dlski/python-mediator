import inspect
import sys
from dataclasses import dataclass
from inspect import Parameter
from typing import Annotated, Any, ForwardRef, get_args, get_origin, get_type_hints

if sys.version_info >= (3, 14):
    import annotationlib

    _FORWARDREF = annotationlib.Format.FORWARDREF


@dataclass(frozen=True)
class CallableArg:
    """
    Stores information about given callable argument.
    """

    # argument name
    name: str
    # argument type annotation
    type: Any | None
    # argument is positional flag
    is_positional: bool


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class CallableIODetails:
    """
    Stores all information about input arguments and output data type.
    """

    # list of callable arguments details
    args: list[CallableArg]
    # when True callable accepts variadic keyword args like **kwargs
    has_kwargs: bool
    # return type annotation
    return_type: Any | None

    def arg_by_name(self, name: str) -> CallableArg | None:
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


@dataclass(frozen=True)
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
        signature = _signature(fn)
        annotations = _type_hints(fn)
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


def _type_hints(fn: Any) -> dict[str, Any]:
    """
    Provides resolved annotations of given callable.

    Works like `typing.get_type_hints`, but annotation that cannot be resolved
    (i.e. name imported only for type checking) does not fail the other ones.
    Such annotation is omitted in result.
    :param fn: callable to inspect
    :return: argument name (or `return`) to resolved annotation mapping
    """
    try:
        return get_type_hints(fn)
    except (NameError, AttributeError):
        pass

    globalns = getattr(inspect.unwrap(fn), "__globals__", {})
    hints: dict[str, Any] = {}
    for name, annotation in _raw_annotations(fn).items():
        if isinstance(annotation, str):
            try:
                annotation = eval(annotation, globalns)
            except Exception:
                continue
        elif isinstance(annotation, ForwardRef):
            continue
        if get_origin(annotation) is Annotated:
            annotation = get_args(annotation)[0]
        hints[name] = annotation
    return hints


def _signature(fn: Any) -> inspect.Signature:
    """
    Provides signature of given callable without failing on unresolvable annotations.
    :param fn: callable to inspect
    :return: callable signature
    """
    if sys.version_info >= (3, 14):
        # annotations are evaluated lazily, so reading them may fail
        return inspect.signature(fn, annotation_format=_FORWARDREF)
    return inspect.signature(fn)


def _raw_annotations(fn: Any) -> dict[str, Any]:
    """
    Provides annotations of given callable without failing on unresolvable ones.
    :param fn: callable to inspect
    :return: argument name (or `return`) to annotation mapping,
    where not evaluated annotation is a string or forward reference object
    """
    if sys.version_info >= (3, 14):
        return annotationlib.get_annotations(fn, format=_FORWARDREF)
    return inspect.get_annotations(fn)
