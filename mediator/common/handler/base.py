from typing import Hashable

from mediator.common.types import ActionResult, ActionSubject


class HandlerInfo:
    @property
    def key(self) -> Hashable:
        raise NotImplementedError


class Handler(HandlerInfo):
    @property
    def key(self) -> Hashable:
        raise NotImplementedError

    async def __call__(self, action: ActionSubject) -> ActionResult:
        raise NotImplementedError
