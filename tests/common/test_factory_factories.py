import pytest

from mediator.common.factory import (
    CallableHandlerFactory,
    CallableHandlerPolicy,
    MethodHandlerFactory,
    MethodHandlerPolicy,
)
from mediator.common.handler import Handler
from mediator.common.types import ActionResult, ActionSubject


class _Base:
    pass


class _A(_Base):
    async def a(self, arg: str, x: int, y: int):
        return arg, x, y

    async def b(self, *, arg: str, a: int, b: int):
        return arg, a, b


async def _check_handler(handler: Handler):
    action = ActionSubject(subject="test", inject={"x": 1, "y": 2})
    result: ActionResult = await handler(action)
    assert result.result == ("test", 1, 2)


@pytest.mark.parametrize(
    "obj, policy",
    [
        (_A().a, CallableHandlerPolicy()),
        (_A().b, CallableHandlerPolicy(arg_map={"x": "a", "y": "b"})),
    ],
)
@pytest.mark.asyncio
async def test_callable_handler_factory(obj, policy: CallableHandlerPolicy):
    factory = CallableHandlerFactory(policy)
    handler = factory.create(obj)
    await _check_handler(handler)


@pytest.mark.parametrize(
    "obj, policy",
    [
        (_A(), MethodHandlerPolicy(name="a")),
        (
            _A(),
            MethodHandlerPolicy(
                name="b",
                subtype_of=[_Base],
                policy=CallableHandlerPolicy(arg_map={"x": "a", "y": "b"}),
            ),
        ),
    ],
)
@pytest.mark.asyncio
async def test_method_handler_factory(obj, policy: MethodHandlerPolicy):
    factory = MethodHandlerFactory(policy)
    handler = factory.create(obj)
    await _check_handler(handler)
