from typing import Sequence

from mediator.common.types import ActionCallType


class OperatorDef:
    def create(self, call: ActionCallType, **kwargs) -> ActionCallType:
        raise NotImplementedError


class OperatorStack:
    @classmethod
    def build(
        cls, op_defs: Sequence[OperatorDef], call: ActionCallType
    ) -> ActionCallType:
        target = call
        for op_def in reversed(op_defs):
            call = op_def.create(call, target=target)
        return call
