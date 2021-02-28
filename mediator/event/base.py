from typing import Any, AsyncContextManager, Iterable

from mediator.common.registry import HandlerEntry, HandlerStore
from mediator.utils.context import AsyncNullContextManager


class EventPublish:
    async def publish(self, obj: Any, **kwargs):
        raise NotImplementedError


class EventPublisher(EventPublish):
    # noinspection PyMethodMayBeStatic
    def transaction(self) -> AsyncContextManager[EventPublish]:
        return AsyncNullContextManager(self)

    async def publish(self, obj: Any, **kwargs):
        raise NotImplementedError


class EventSubscriber(HandlerStore):
    def add(self, entry: HandlerEntry):
        raise NotImplementedError

    def include(self, entries: Iterable[HandlerEntry]):
        raise NotImplementedError

    def __iter__(self) -> Iterable[HandlerEntry]:
        raise NotImplementedError
