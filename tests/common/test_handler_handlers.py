import pytest

from mediator.common.handler import DirectHandler, MappedDirectHandler
from mediator.common.types import ActionResult, ActionSubject


async def _fn(*args, **kwargs):
    return args, kwargs


class SpecificError(Exception):
    pass


async def _error_fn(*arg, **kwargs):
    raise SpecificError(f"{arg} {kwargs}")


def _result(*args, **kwargs):
    return args, kwargs


@pytest.fixture
def action():
    return ActionSubject(subject="test", inject={"a": 10, "b": 20})


@pytest.mark.asyncio
async def test_direct_handler_call(action: ActionSubject):
    handler = DirectHandler(handler=_fn, fn=_fn, key=str)
    assert handler.key == str
    result = await handler(action)
    assert isinstance(result, ActionResult)
    assert result.result == _result("test", a=10, b=20)


@pytest.mark.asyncio
async def test_direct_handler_error(action: ActionSubject):
    handler = DirectHandler(handler=_error_fn, fn=_error_fn, key=str)
    with pytest.raises(SpecificError):
        await handler(action)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "subject_name, arg_map, expected_result",
    [
        (None, {}, _result("test", a=10, b=20)),
        ("subject", {}, _result(subject="test", a=10, b=20)),
        (None, {"a": "x"}, _result("test", x=10, b=20)),
        ("subject", {"a": "x", "b": "y"}, _result(subject="test", x=10, y=20)),
    ],
)
async def test_mapped_direct_handler_call(
    action, subject_name, arg_map, expected_result
):
    handler = MappedDirectHandler(
        handler=_fn, fn=_fn, key=str, subject_name=subject_name, arg_map=arg_map
    )
    assert handler.key == str
    result = await handler(action)
    assert isinstance(result, ActionResult)
    assert result.result == expected_result


@pytest.mark.asyncio
async def test_mapped_direct_handler_error(action):
    handler = MappedDirectHandler(
        handler=_error_fn, fn=_error_fn, key=str, subject_name="subject", arg_map={}
    )
    with pytest.raises(SpecificError):
        await handler(action)
