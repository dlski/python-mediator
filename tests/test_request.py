from typing import List

import pytest

from mediator.common.factory import CallableHandlerPolicy
from mediator.common.registry import LookupHandlerStoreError
from mediator.request import LocalRequestBus, RequestHandlerRegistry
from tests.common.common import MockupOperatorDef


class _MockupRequestA:
    pass


class _MockupRequestB:
    pass


# noinspection PyUnusedLocal
async def _handle_a(a: _MockupRequestA, seq: List[str]):
    return seq


# noinspection PyUnusedLocal
async def _handle_b(b: _MockupRequestB, seq: List[str]):
    return seq


@pytest.mark.asyncio
async def test_local_request_executor():
    policies = [CallableHandlerPolicy()]
    executor = LocalRequestBus(
        policies=policies, operators=MockupOperatorDef.operators("abc")
    )
    executor.register(_handle_a)

    registry = RequestHandlerRegistry(
        policies=policies, operators=MockupOperatorDef.operators("xyz")
    )
    registry.register(_handle_b)
    executor.include(registry)

    for rq, expected_seq in [
        (_MockupRequestA(), list("abc")),
        (_MockupRequestB(), list("abcxyz")),
    ]:
        result_seq = await executor.execute(rq, seq=[])
        assert result_seq == expected_seq

    with pytest.raises(LookupHandlerStoreError):
        await executor.execute(object())
