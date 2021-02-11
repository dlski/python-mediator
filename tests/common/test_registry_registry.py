from typing import Callable, Sequence

import pytest

from mediator.common.factory import (
    CallableHandlerPolicy,
    DefaultHandlerFactoryMapper,
    HandlerFactoryCascade,
    IncompatibleHandlerFactoryCascadeError,
    MethodHandlerPolicy,
    PolicyType,
)
from mediator.common.operators import OperatorDef
from mediator.common.registry import CollectionHandlerStore, HandlerRegistry
from tests.common.common import MockupOperatorDef, mockup_action, mockup_handle


class _A:
    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    async def handle(self, arg: str, **kwargs):
        return arg


# noinspection PyUnusedLocal
async def _handle(arg: str, **kwargs):
    return arg


def test_handler_registry_config_error():
    with pytest.raises(TypeError):
        HandlerRegistry(store=CollectionHandlerStore())


def _registry_cascade_factory():
    return HandlerRegistry(
        store=CollectionHandlerStore(),
        cascade=HandlerFactoryCascade(
            policies=[CallableHandlerPolicy()],
            mapper=DefaultHandlerFactoryMapper(),
        ),
    )


def _registry_policies_factory():
    return HandlerRegistry(
        store=CollectionHandlerStore(),
        policies=[CallableHandlerPolicy()],
    )


@pytest.mark.parametrize(
    "registry_factory",
    [_registry_cascade_factory, _registry_policies_factory],
)
@pytest.mark.parametrize(
    "policies, incompatible, compatible",
    [
        (None, _A(), _handle),
        ([MethodHandlerPolicy(name="handle")], _handle, _A()),
    ],
)
@pytest.mark.asyncio
async def test_handler_registry_policy(
    registry_factory: Callable[[], HandlerRegistry],
    incompatible,
    compatible,
    policies: Sequence[PolicyType],
):
    registry = registry_factory()

    with pytest.raises(IncompatibleHandlerFactoryCascadeError):
        registry.register(incompatible, policies=policies)

    with pytest.raises(IncompatibleHandlerFactoryCascadeError):
        registry.register(policies=policies)(incompatible)

    registry.register(compatible, policies=policies)
    registry.register(policies=policies)(compatible)

    for entry in registry:
        call = entry.handler_pipeline()
        result = await call(mockup_action())
        assert result.result == "test"


@pytest.mark.parametrize(
    "global_operators, local_operators, seq",
    [
        (MockupOperatorDef.operators("abc"), (), list("abc")),
        ((), MockupOperatorDef.operators("xyz"), list("xyz")),
        (
            MockupOperatorDef.operators("abc"),
            MockupOperatorDef.operators("xyz"),
            list("abcxyz"),
        ),
    ],
)
@pytest.mark.asyncio
async def test_handler_operators(
    global_operators: Sequence[OperatorDef],
    local_operators: Sequence[OperatorDef],
    seq: Sequence[str],
):
    registry = HandlerRegistry(
        store=CollectionHandlerStore(),
        policies=[CallableHandlerPolicy()],
        operators=global_operators,
    )
    registry.register(mockup_handle, operators=local_operators)
    registry.register(operators=local_operators)(mockup_handle)
    for entry in registry:
        call = entry.handler_pipeline()
        result = await call(mockup_action())
        assert result.result == seq
