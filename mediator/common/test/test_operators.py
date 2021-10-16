from typing import Collection

import pytest

from mediator.common.operators import OperatorDef, OperatorStack
from mediator.common.types import ActionCallType, ActionResult, ActionSubject


class MockupOperatorDef(OperatorDef):
    def __init__(self, seq_item: str):
        self.seq_item = seq_item

    def create(self, call: ActionCallType, **kwargs) -> ActionCallType:
        seq_item = self.seq_item

        async def _op(action: ActionSubject):
            if "seq" not in action.inject:
                action.inject["seq"] = []
            seq = action.inject["seq"]
            seq.append(seq_item)
            return await call(action)

        return _op

    @classmethod
    def operators(cls, seq: Collection[str]):
        return [cls(seq_item) for seq_item in seq]


@pytest.fixture
def action():
    return ActionSubject(subject="test", inject={})


async def _get_seq_call(action: ActionSubject):
    return ActionResult(action.inject["seq"])


@pytest.mark.asyncio
async def test_operator_stack(action: ActionSubject):
    letters = ["x", "y", "z"]
    operators = MockupOperatorDef.operators(letters)
    call = OperatorStack.build(operators, _get_seq_call)
    result = await call(action)
    assert result.result == letters
