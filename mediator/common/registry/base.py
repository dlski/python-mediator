from dataclasses import dataclass
from typing import Iterable, Sequence

from mediator.common.handler.base import Handler
from mediator.common.operators import OperatorDef, OperatorStack
from mediator.common.types import ActionCallType


@dataclass
class HandlerEntry:
    handler: Handler
    operators: Sequence[OperatorDef] = ()

    @property
    def key(self):
        return self.handler.key

    def handler_pipeline(self) -> ActionCallType:
        return self.pipeline(self.handler)

    def pipeline(self, call: ActionCallType) -> ActionCallType:
        return OperatorStack.build(self.operators, call)

    def stack(self, operators: Sequence[OperatorDef]) -> "HandlerEntry":
        return HandlerEntry(
            handler=self.handler,
            operators=tuple([*operators, *self.operators]),
        )


class HandlerStoreError(Exception):
    pass


class InspectionHandlerStoreError(HandlerStoreError):
    pass


class CollisionHandlerStoreError(KeyError, HandlerStoreError):
    pass


class LookupHandlerStoreError(LookupError, HandlerStoreError):
    pass


class HandlerStore:
    def add(self, entry: HandlerEntry):
        raise NotImplementedError

    def include(self, entries: Iterable[HandlerEntry]):
        raise NotImplementedError

    def __iter__(self) -> Iterable[HandlerEntry]:
        raise NotImplementedError
