import pytest

from mediator.common.operators import OperatorDef, OperatorStack
from tests.common.common import MockupOperatorDef, mockup_action, mockup_call


def test_operator_def():
    with pytest.raises(TypeError):
        hash(OperatorDef())


@pytest.mark.asyncio
async def test_operator_stack():
    letters = list("xyz")
    operators = MockupOperatorDef.operators(letters)
    call = OperatorStack.build(operators, mockup_call)
    result = await call(mockup_action())
    assert result.result == letters
