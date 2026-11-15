from collections.abc import Sequence
from types import NoneType, UnionType
from typing import Any, Union, get_args, get_origin

from mediator.common.factory.base import (
    HandlerFactoryError,
    IncompatibleHandlerFactoryError,
)
from mediator.common.factory.policies import CallableHandlerPolicy
from mediator.common.handler import CallableHandler, Handler
from mediator.utils.inspection import CallableArg, CallableDetails, CallableInspector


def inspect_callable(obj: Any) -> CallableDetails:
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
        raise IncompatibleHandlerFactoryError(f"{obj!r}: {e}") from e


def inspect_attribute(
    obj: Any, name: str, subtype_of: Sequence[type] = ()
) -> CallableDetails:
    """
    (Optionally) checks if object has valid type
    and performs callable inspection for given object attribute.
    :param obj: input object
    :param name: inspection object attribute name
    :param subtype_of: sequence of types to check
    if an instance of an input object is one of them;
    just like `isinstance(obj, subtype_of)`
    :raises IncompatibleHandlerFactoryError: when object type is not supported
    :raises IncompatibleHandlerFactoryError:
    when object has no attribute with expected name
    :raises IncompatibleHandlerFactoryError:
    when expected attribute is not callable
    :return: callable object attribute `CallableDetails` result
    """
    if subtype_of and not isinstance(obj, tuple(subtype_of)):
        raise IncompatibleHandlerFactoryError(
            f"Object {obj!r} is not type of {tuple(subtype_of)}"
        )

    try:
        attr = getattr(obj, name)
    except AttributeError:
        raise IncompatibleHandlerFactoryError(
            f"Object {obj!r} has no attribute named {name}"
        ) from None

    try:
        return CallableInspector.inspect(attr)
    except TypeError as e:
        raise IncompatibleHandlerFactoryError(f"{obj!r} attribute {name}: {e}") from e


def find_subject_arg(details: CallableDetails, name: str | None = None) -> CallableArg:
    """
    Finds primary argument for given callable,
    to be filled with action subject (event, request, command etc object).
    :param details: callable details to use
    :param name: optional argument name hint;
    when provided argument with that name is assumed as primary,
    otherwise first callable argument is used
    :raises IncompatibleHandlerFactoryError: when callable has no arguments
    :raises IncompatibleHandlerFactoryError: when argument name was specified,
    but no matching argument was found
    :return: primary argument details
    """
    if not details.args:
        raise IncompatibleHandlerFactoryError(
            f"Callable {details.obj!r} has no explicit argument"
        )

    if name:
        arg = details.arg_by_name(name)
        if arg is None:
            raise IncompatibleHandlerFactoryError(
                f"Callable {details.obj!r} has no argument named {name}"
            )
    else:
        arg = details.args[0]
    return arg


def subject_types(details: CallableDetails, arg: CallableArg) -> tuple[type, ...]:
    """
    Provides action subject types accepted by given primary callable argument.
    :param details: callable details
    :param arg: primary argument details
    :raises HandlerFactoryError: when argument has no type annotation
    or its type annotation cannot be resolved
    :raises HandlerFactoryError: when argument type annotation
    is not a type or union of types
    :return: single type or all types of union (like `A | B`) in declared order
    """
    annotation = arg.type
    if annotation is None:
        raise HandlerFactoryError(
            f"Callable {details.obj!r} argument {arg.name} has no type annotation"
            f" or it cannot be resolved"
        )

    types: tuple[Any, ...]
    if get_origin(annotation) in (Union, UnionType):
        types = get_args(annotation)
    else:
        types = (annotation,)

    if not all(isinstance(type_, type) and type_ is not NoneType for type_ in types):
        raise HandlerFactoryError(
            f"Callable {details.obj!r} argument {arg.name}"
            f" type annotation is not a type or union of types"
        )
    return types


def create_callable_handlers(
    details: CallableDetails, obj: Any, policy: CallableHandlerPolicy
) -> Sequence[Handler]:
    """
    Creates callable handlers using given specification:
    one for every action subject type accepted by callable.
    :param details: details of callable to be invoked by handler
    :param obj: underlying object
    - source of callable object and handler behaviour information object
    :param policy: specification how handler should invoke callable
    :raises IncompatibleHandlerFactoryError:
    when callable has no usable primary (subject) argument
    :raises HandlerFactoryError:
    when for primary (subject) argument cannot be determined unequivocal type
    :raises HandlerFactoryError: when callable object is not async callable
    :return: handler objects that can call underlying callable using provided action
    """
    arg = find_subject_arg(details, policy.subject_arg)
    types = subject_types(details, arg)
    if not details.is_async:
        raise HandlerFactoryError(f"Object {details.obj!r} is not async callable")

    subject_name: str | None
    if policy.subject_as_keyword or not arg.is_positional:
        # subject has to be provided as keyword argument
        subject_name = arg.name
    else:
        subject_name = None

    allow_args: set[str] | None
    if policy.arg_strict or details.has_kwargs:
        # all action arguments are provided for callable
        allow_args = None
    else:
        # only arguments that fit into callable signature are provided
        allow_args = {arg.name for arg in details.args}

    return [
        CallableHandler(
            obj=obj,
            fn=details.obj,
            key=type_,
            subject_name=subject_name,
            arg_map=policy.arg_map,
            allow_args=allow_args,
        )
        for type_ in types
    ]
