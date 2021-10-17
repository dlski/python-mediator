from typing import Callable, List, Sequence

import pytest

from mediator.common.factory import (
    CallableHandlerPolicy,
    DefaultHandlerFactoryMapper,
    HandlerFactoryCascade,
    IncompatibleHandlerFactoryCascadeError,
    MethodHandlerPolicy,
    PolicyType,
)
from mediator.common.modifiers import ModifierFactory
from mediator.common.registry import CollectionHandlerStore, HandlerRegistry
from mediator.common.test.test_modifiers import MockupModifierFactory
from mediator.common.types import ActionSubject


def test_handler_registry_config_error():
    with pytest.raises(TypeError):
        HandlerRegistry(store=CollectionHandlerStore())


class _A:
    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    async def handle(self, arg: str, **kwargs):
        return arg


# noinspection PyUnusedLocal
async def _handle(arg: str, **kwargs):
    return arg


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
    mockup_action_factory: Callable[[], ActionSubject],
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
        result = await call(mockup_action_factory())
        assert result.result == "test"


async def _return_seq(_: str, seq: List[str]):
    return seq


@pytest.mark.parametrize(
    "global_modifiers, local_modifiers, seq",
    [
        (MockupModifierFactory.modifiers("abc"), (), list("abc")),
        ((), MockupModifierFactory.modifiers("xyz"), list("xyz")),
        (
            MockupModifierFactory.modifiers("abc"),
            MockupModifierFactory.modifiers("xyz"),
            list("abcxyz"),
        ),
    ],
)
@pytest.mark.asyncio
async def test_handler_modifiers(
    global_modifiers: Sequence[ModifierFactory],
    local_modifiers: Sequence[ModifierFactory],
    seq: Sequence[str],
    mockup_action_factory: Callable[[], ActionSubject],
):
    registry = HandlerRegistry(
        store=CollectionHandlerStore(),
        policies=[CallableHandlerPolicy()],
        modifiers=global_modifiers,
    )
    registry.register(_return_seq, modifiers=local_modifiers)
    registry.register(modifiers=local_modifiers)(_return_seq)
    for entry in registry:
        call = entry.handler_pipeline()
        result = await call(mockup_action_factory())
        assert result.result == seq
