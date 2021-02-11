import pytest

from mediator.common.registry import HandlerEntry
from tests.common.common import (
    MockupHandler,
    MockupOperatorDef,
    mockup_action,
    mockup_call,
)


@pytest.mark.asyncio
async def test_handler_entry():
    standard_seq = list("xyz")
    extended_seq = list("abc")
    overall_seq = extended_seq + standard_seq
    entry = HandlerEntry(
        handler=MockupHandler(str),
        operators=MockupOperatorDef.operators(standard_seq),
    )
    assert entry.key is str

    handler_call = entry.handler_pipeline()
    result = await handler_call(mockup_action())
    assert result.result == ("test", {"seq": standard_seq})

    call = entry.pipeline(mockup_call)
    result = await call(mockup_action())
    assert result.result == standard_seq

    extended_entry = entry.stack(operators=MockupOperatorDef.operators(extended_seq))
    assert extended_entry.handler == entry.handler
    for operator, seq_id in zip(extended_entry.operators, overall_seq):
        assert isinstance(operator, MockupOperatorDef)
        assert operator.seq_id == seq_id
    call = extended_entry.pipeline(mockup_call)
    result = await call(mockup_action())
    assert result.result == overall_seq
