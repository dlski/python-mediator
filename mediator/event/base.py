from typing import Any, Iterable

from mediator.common.registry import HandlerEntry, HandlerStore


class EventPublisher:
    async def publish(self, obj: Any, **kwargs):
        raise NotImplementedError


class EventSubscriber(HandlerStore):
    def add(self, entry: HandlerEntry):
        raise NotImplementedError

    def include(self, entries: Iterable[HandlerEntry]):
        raise NotImplementedError

    def __iter__(self) -> Iterable[HandlerEntry]:
        raise NotImplementedError
