from typing import Callable

import pytest

from mediator.common.registry import HandlerEntry
from mediator.common.registry.test.conftest import MockupHandler
from mediator.common.test.test_operators import MockupOperatorDef
from mediator.common.types import ActionResult, ActionSubject


async def _return_seq(subject: ActionSubject) -> ActionResult:
    return ActionResult(result=subject.inject["seq"])


@pytest.mark.asyncio
async def test_handler_entry(mockup_action_factory: Callable[[], ActionSubject]):
    standard_seq = list("xyz")
    extended_seq = list("abc")
    overall_seq = extended_seq + standard_seq
    entry = HandlerEntry(
        handler=MockupHandler(str),
        operators=MockupOperatorDef.operators(standard_seq),
    )
    assert entry.key is str

    handler_call = entry.handler_pipeline()
    result = await handler_call(mockup_action_factory())
    assert result.result == ("test", {"seq": standard_seq})

    call = entry.pipeline(_return_seq)
    result = await call(mockup_action_factory())
    assert result.result == standard_seq

    extended_entry = entry.stack(operators=MockupOperatorDef.operators(extended_seq))
    assert extended_entry.handler == entry.handler
    for operator, seq_item in zip(extended_entry.operators, overall_seq):
        assert isinstance(operator, MockupOperatorDef)
        assert operator.seq_item == seq_item
    call = extended_entry.pipeline(_return_seq)
    result = await call(mockup_action_factory())
    assert result.result == overall_seq
