from typing import Hashable, Iterable, Sequence

from mediator.common.handler import Handler
from mediator.common.operators import OperatorDef
from mediator.common.types import ActionCallType, ActionResult, ActionSubject


class MockupHandler(Handler):
    def __init__(self, key: Hashable):
        self._key = key

    async def __call__(self, action: ActionSubject) -> ActionResult:
        return ActionResult(result=(action.subject, action.inject))

    @property
    def key(self) -> Hashable:
        return self._key

    @staticmethod
    def result(arg, **kwargs):
        return arg, kwargs


class MockupOperatorDef(OperatorDef):
    def __init__(self, seq_id: str):
        self.seq_id = seq_id

    def __hash__(self):
        return hash((type(self), self.seq_id))

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.seq_id == other.seq_id

    def create(self, call: ActionCallType, **kwargs) -> ActionCallType:
        async def _op(action: ActionSubject):
            seq = action.inject.get("seq")
            assert isinstance(seq, list), "'seq' list not provided"
            seq.append(self.seq_id)
            return await call(action)

        return _op

    @classmethod
    def operators(cls, seq: Iterable[str]):
        return [cls(seq_id) for seq_id in seq]


def mockup_action():
    return ActionSubject(subject="test", inject={"seq": []})


async def mockup_call(action: ActionSubject):
    return ActionResult(action.inject["seq"])


# noinspection PyUnusedLocal
async def mockup_handle(arg: str, seq: Sequence[str]):
    return seq
