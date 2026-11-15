from typing import Any

import pytest

from mediator.common.factory import CallableHandlerPolicy
from mediator.common.registry import LookupHandlerStoreError
from mediator.common.types import ActionCallType, ActionSubject
from mediator.request import LocalRequestBus, RequestHandlerRegistry
from tests.common.test_modifiers import MockupModifierFactory


class _RequestA:
    pass


class _RequestB:
    pass


# noinspection PyUnusedLocal
async def _handle_a(a: _RequestA, seq: list[str]):
    return seq


# noinspection PyUnusedLocal
async def _handle_b(b: _RequestB, seq: list[str]):
    return seq


@pytest.mark.asyncio
async def test_local_request_executor():
    policies = [CallableHandlerPolicy()]
    executor = LocalRequestBus(
        policies=policies, modifiers=MockupModifierFactory.modifiers("abc")
    )
    executor.register(_handle_a)

    registry = RequestHandlerRegistry(
        policies=policies, modifiers=MockupModifierFactory.modifiers("xyz")
    )
    registry.register(_handle_b)
    executor.include(registry)

    for rq, expected_seq in [
        (_RequestA(), list("abc")),
        (_RequestB(), list("abcxyz")),
    ]:
        result_seq = await executor.execute(rq, seq=[])
        assert result_seq == expected_seq

    with pytest.raises(LookupHandlerStoreError):
        await executor.execute(object())


@pytest.mark.asyncio
async def test_local_request_executor_include_iterator():
    registry = RequestHandlerRegistry()
    registry.register(_handle_a)

    executor = LocalRequestBus()
    executor.include(iter(registry))
    assert await executor.execute(_RequestA(), seq=["x"]) == ["x"]


class _BrokenModifierFactory:
    def create(self, call: ActionCallType, *, target: ActionCallType) -> ActionCallType:
        async def _op(action: ActionSubject) -> Any:
            return (await call(action)).result

        return _op


@pytest.mark.asyncio
async def test_local_request_executor_result_type():
    executor = LocalRequestBus(modifiers=[_BrokenModifierFactory()])
    executor.register(_handle_a)
    with pytest.raises(TypeError, match="ActionResult"):
        await executor.execute(_RequestA(), seq=[])
