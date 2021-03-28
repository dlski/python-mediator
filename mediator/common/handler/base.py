from typing import Any, Hashable

from mediator.common.types import ActionResult, ActionSubject


class HandlerInfo:
    @property
    def key(self) -> Hashable:
        raise NotImplementedError

    @property
    def obj(self) -> Any:
        raise NotImplementedError


class Handler(HandlerInfo):
    @property
    def key(self) -> Hashable:
        raise NotImplementedError

    @property
    def obj(self) -> Any:
        raise NotImplementedError

    async def __call__(self, action: ActionSubject) -> ActionResult:
        raise NotImplementedError
