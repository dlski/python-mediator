from collections.abc import Sequence
from dataclasses import replace
from typing import Union

import pytest

from mediator.common.factory import (
    CallableHandlerPolicy,
    HandlerFactoryError,
    IncompatibleHandlerFactoryError,
)
from mediator.common.factory.utils import (
    create_callable_handlers,
    find_subject_arg,
    inspect_attribute,
    inspect_callable,
    subject_types,
)
from mediator.common.types import ActionResult, ActionSubject


class _A:
    pass


class _B(_A):
    def method_no_args(self):
        return

    # noinspection PyUnusedLocal
    def method(self, one: str, two: int, three: str | None, four) -> _A:
        return self


class _C:
    def __init__(self):
        self.method = 1

    @staticmethod
    async def async_call(*args, **kwargs):
        return args, kwargs

    @staticmethod
    async def a_signature(arg: str, x: int, y: int):
        pass

    @staticmethod
    async def b_signature(*, arg: str, x: int, y: int):
        pass

    @staticmethod
    async def c_signature(arg: str, a: int, b: int):
        pass

    @staticmethod
    def sync_call(arg: str, x: int, y: int):
        pass


def test_callable_obj_details():
    assert inspect_callable(_B().method).return_type == _A

    with pytest.raises(IncompatibleHandlerFactoryError) as e:
        inspect_callable(_A())
    assert "not callable" in str(e.value)


@pytest.mark.parametrize(
    ("obj", "subtype_of", "error", "error_message"),
    [
        (_B(), (), None, None),
        (_A(), (), IncompatibleHandlerFactoryError, "no attribute"),
        (_C(), (), IncompatibleHandlerFactoryError, "not callable"),
        (_B(), [_A], None, None),
        (_C(), [_A], IncompatibleHandlerFactoryError, "not type of"),
    ],
)
def test_callable_attribute_details(
    obj,
    subtype_of: Sequence[type],
    error: type[Exception] | None,
    error_message: str | None,
):
    if error:
        with pytest.raises(error) as e:
            inspect_attribute(obj, "method", subtype_of)
        if error_message:
            assert error_message in str(e.value)
    else:
        details = inspect_attribute(obj, "method", subtype_of)
        assert details.return_type == _A


@pytest.mark.parametrize(
    ("obj", "name", "expected_name", "error", "error_message"),
    [
        (_B().method, None, "one", None, None),
        (_B().method, "two", "two", None, None),
        (
            _B().method_no_args,
            None,
            None,
            IncompatibleHandlerFactoryError,
            "no explicit argument",
        ),
        (
            _B().method,
            "not_found",
            "not_found",
            IncompatibleHandlerFactoryError,
            "no argument named",
        ),
        (_B().method, "four", "four", HandlerFactoryError, "no type annotation"),
        (
            _B().method,
            "three",
            "three",
            HandlerFactoryError,
            "type annotation is not a type",
        ),
    ],
)
def test_subject_arg_get(
    obj,
    name: str | None,
    expected_name,
    error: type[Exception] | None,
    error_message: str | None,
):
    details = inspect_callable(obj)
    if error:
        with pytest.raises(error) as e:
            subject_types(details, find_subject_arg(details, name))
        if error_message:
            assert error_message in str(e.value)
    else:
        arg = find_subject_arg(details, name)
        assert arg.name == expected_name


def _result(*args, **kwargs):
    return args, kwargs


@pytest.mark.parametrize(
    ("obj", "sig", "name", "arg_map", "expected_result"),
    [
        (_C.async_call, _C.a_signature, None, {}, _result("test", x=1, y=2)),
        (_C.async_call, _C.a_signature, "arg", {}, _result(arg="test", x=1, y=2)),
        (_C.async_call, _C.b_signature, None, {}, _result(arg="test", x=1, y=2)),
        (
            _C.async_call,
            _C.c_signature,
            None,
            {"x": "a", "y": "b"},
            _result("test", a=1, b=2),
        ),
    ],
)
@pytest.mark.asyncio
async def test_direct_handler_create_successful(
    obj,
    sig,
    name: str | None,
    arg_map: dict[str, str],
    expected_result,
):
    policy = CallableHandlerPolicy(subject_arg=name, arg_map=arg_map, arg_strict=True)
    details = replace(inspect_callable(sig), obj=obj)
    [handler] = create_callable_handlers(details, obj=obj, policy=policy)

    result = await handler(ActionSubject(subject="test", inject={"x": 1, "y": 2}))
    assert isinstance(result, ActionResult)
    assert result.result == expected_result


@pytest.mark.parametrize(
    ("obj", "error", "error_message"),
    [
        (_C.sync_call, HandlerFactoryError, "not async callable"),
    ],
)
def test_direct_handler_create_fail(obj, error, error_message):
    policy = CallableHandlerPolicy(subject_arg="arg", arg_strict=True)
    details = inspect_callable(obj)
    with pytest.raises(error) as e:
        create_callable_handlers(details, obj=obj, policy=policy)
    assert error_message in str(e.value)


class _D:
    @staticmethod
    async def union(arg: _A | _C, x: int):
        pass

    @staticmethod
    async def typing_union(arg: Union[_A, _C], x: int):  # noqa: UP007
        pass

    @staticmethod
    async def single(arg: _A, x: int):
        pass

    @staticmethod
    async def unresolvable(arg: "Missing", x: int):  # type: ignore[name-defined]  # noqa: F821
        pass

    @staticmethod
    async def generic(arg: list[_A], x: int):
        pass


@pytest.mark.parametrize(
    ("obj", "expected_types"),
    [
        (_D.union, (_A, _C)),
        (_D.typing_union, (_A, _C)),
        (_D.single, (_A,)),
    ],
)
def test_subject_types(obj, expected_types: tuple[type, ...]):
    details = inspect_callable(obj)
    arg = find_subject_arg(details)
    assert subject_types(details, arg) == expected_types

    handlers = create_callable_handlers(
        details, obj=obj, policy=CallableHandlerPolicy()
    )
    assert tuple(handler.key for handler in handlers) == expected_types


@pytest.mark.parametrize(
    ("obj", "error_message"),
    [
        (_D.unresolvable, "cannot be resolved"),
        (_D.generic, "not a type or union of types"),
    ],
)
def test_subject_types_fail(obj, error_message: str):
    details = inspect_callable(obj)
    arg = find_subject_arg(details)
    with pytest.raises(HandlerFactoryError) as e:
        subject_types(details, arg)
    assert error_message in str(e.value)
