from typing import Dict, Optional, Sequence, Type

import pytest

from mediator.common.factory import HandlerFactoryError, IncompatibleHandlerFactoryError
from mediator.common.factory.utils import (
    CallableAttributeDetails,
    CallableObjDetails,
    DirectHandlerCreate,
    HandlerSubjectArgGet,
)
from mediator.common.types import ActionResult, ActionSubject


class _A:
    pass


class _B(_A):
    def method_no_args(self):
        return

    # noinspection PyUnusedLocal
    def method(self, one: str, two: int, three: Optional[str], four) -> _A:
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
    get_details = CallableObjDetails()

    assert get_details(_B().method).return_type == _A

    with pytest.raises(IncompatibleHandlerFactoryError) as e:
        get_details(_A())
    assert "not callable" in str(e.value)


@pytest.mark.parametrize(
    "obj, subtype_of, error, error_message",
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
    subtype_of: Sequence[Type],
    error: Optional[Type[Exception]],
    error_message: Optional[str],
):
    get_details = CallableAttributeDetails(name="method", owner_subtype_of=subtype_of)
    if error:
        with pytest.raises(error) as e:
            get_details(obj)
        if error_message:
            assert error_message in str(e.value)
    else:
        details = get_details(obj)
        assert details.return_type == _A


@pytest.mark.parametrize(
    "obj, name, expected_name, error, error_message",
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
    name: Optional[str],
    expected_name,
    error: Optional[Type[Exception]],
    error_message: Optional[str],
):
    get_details = CallableObjDetails()
    arg_get = HandlerSubjectArgGet(name=name)

    details = get_details(obj)
    if error:
        with pytest.raises(error) as e:
            arg_get(details)
        if error_message:
            assert error_message in str(e.value)
    else:
        arg = arg_get(details)
        assert arg.name == expected_name


def _result(*args, **kwargs):
    return args, kwargs


@pytest.mark.parametrize(
    "obj, sig, name, arg_map, expected_result",
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
    name: Optional[str],
    arg_map: Dict[str, str],
    expected_result,
):
    get_details = CallableObjDetails()
    arg_get = HandlerSubjectArgGet(name=name)
    handler_create = DirectHandlerCreate(
        subject_as_keyword=name is not None,
        arg_map=arg_map,
        arg_strict=True,
    )

    details = get_details(sig)
    arg = arg_get(details)
    details.obj = obj
    handler = handler_create(details, arg, obj)

    result = await handler(ActionSubject(subject="test", inject={"x": 1, "y": 2}))
    assert isinstance(result, ActionResult)
    assert result.result == expected_result


@pytest.mark.parametrize(
    "obj, error, error_message",
    [
        (_C.sync_call, HandlerFactoryError, "not async callable"),
    ],
)
def test_direct_handler_create_fail(obj, error, error_message):
    get_details = CallableObjDetails()
    arg_get = HandlerSubjectArgGet(name="arg")
    handler_create = DirectHandlerCreate(
        subject_as_keyword=False, arg_map={}, arg_strict=True
    )

    details = get_details(obj)
    arg = arg_get(details)
    with pytest.raises(error) as e:
        handler_create(details, arg, obj)
    assert error_message in str(e.value)
