from typing import Any, Dict, List, Optional, Tuple

from mediator.event.base import EventPublisher


class EventAggregateError(Exception):
    pass


class ConfigEventAggregateError(AssertionError, EventAggregateError):
    pass


class EventAggregate:
    _publisher: Optional[EventPublisher]
    _staged: List[Tuple[Any, Dict[str, Any]]]

    def __init__(self):
        self._publisher = None
        self._staged = []

    def use(self, publisher: EventPublisher):
        self._publisher = publisher
        return self

    async def commit(self):
        publisher = self._publisher
        if publisher is None:
            raise ConfigEventAggregateError(f"Publisher is not set in {self!r}")

        async with publisher.transaction() as context:
            for obj, kwargs in self._staged:
                await context.publish(obj, **kwargs)

        self._staged.clear()

    def cleanup(self):
        self._staged.clear()

    def enqueue(self, obj: Any, **kwargs):
        self._staged.append((obj, kwargs))
