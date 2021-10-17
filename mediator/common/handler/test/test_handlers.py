import pytest

from mediator.common.handler import CallableHandler
from mediator.common.types import ActionResult, ActionSubject


@pytest.fixture
def action():
    return ActionSubject(subject="test", inject={"a": 10, "b": 20})


async def _fn(*args, **kwargs):
    return args, kwargs


def _result(*args, **kwargs):
    return args, kwargs


@pytest.mark.parametrize(
    "subject_name, arg_map, allow_args, expected_result",
    [
        (None, {}, None, _result("test", a=10, b=20)),
        ("subject", {}, None, _result(subject="test", a=10, b=20)),
        (None, {"a": "x"}, None, _result("test", x=10, b=20)),
        ("subject", {"a": "x", "b": "y"}, None, _result(subject="test", x=10, y=20)),
        ("subject", {"a": "x", "b": "y"}, {"x"}, _result(subject="test", x=10)),
    ],
)
@pytest.mark.asyncio
async def test_callable_handler_call(
    action: ActionSubject, subject_name, arg_map, allow_args, expected_result
):
    handler = CallableHandler(
        obj=_fn,
        fn=_fn,
        key=str,
        subject_name=subject_name,
        arg_map=arg_map,
        allow_args=allow_args,
    )
    assert handler.key == str
    assert handler.obj == _fn
    result = await handler(action)
    assert isinstance(result, ActionResult)
    assert result.result == expected_result


class _SpecificError(Exception):
    pass


async def _error_fn(*arg, **kwargs):
    raise _SpecificError(f"{arg} {kwargs}")


@pytest.mark.asyncio
async def test_callable_handler_error(action: ActionSubject):
    handler = CallableHandler(
        obj=_error_fn,
        fn=_error_fn,
        key=str,
        subject_name="subject",
        arg_map={},
        allow_args=None,
    )
    with pytest.raises(_SpecificError):
        await handler(action)
