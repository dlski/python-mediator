from typing import List

import pytest

from mediator.common.factory import CallableHandlerPolicy
from mediator.common.registry import LookupHandlerStoreError
from mediator.common.test.test_modifiers import MockupModifierFactory
from mediator.request import LocalRequestBus, RequestHandlerRegistry


class _RequestA:
    pass


class _RequestB:
    pass


# noinspection PyUnusedLocal
async def _handle_a(a: _RequestA, seq: List[str]):
    return seq


# noinspection PyUnusedLocal
async def _handle_b(b: _RequestB, seq: List[str]):
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
