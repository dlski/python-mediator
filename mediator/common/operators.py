from typing import Sequence

from mediator.common.types import ActionCallType


class OperatorDef:
    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self):
        raise TypeError(f"{type(self)} is not hashable")

    def create(self, call: ActionCallType) -> ActionCallType:
        raise NotImplementedError


class OperatorStack:
    @classmethod
    def build(
        cls, op_defs: Sequence[OperatorDef], call: ActionCallType
    ) -> ActionCallType:
        for op_def in reversed(op_defs):
            call = op_def.create(call)
        return call
