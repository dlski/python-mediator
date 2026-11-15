from typing import Any, Dict, List, Optional, Tuple

from mediator.event.base import EventPublisher


class EventAggregateError(Exception):
    """
    Event aggregate base error
    """


class ConfigEventAggregateError(AssertionError, EventAggregateError):
    """
    Config event aggregate error.

    Raised when event aggregate object is not properly configured.
    """


class EventAggregate:
    """
    Event aggregate object.

    Used for staging events and publishing them in one transaction.
    """

    _publisher: Optional[EventPublisher]
    _staged: List[Tuple[Any, Dict[str, Any]]]

    def __init__(self):
        """
        Initializes empty event aggregate.
        """
        self._publisher = None
        self._staged = []

    def use(self, publisher: EventPublisher):
        """
        Sets event publisher used for event sending.
        :param publisher: event publisher to use
        :return: self
        """
        self._publisher = publisher
        return self

    async def commit(self):
        """
        Commits staged events by underlying publisher.
        """
        publisher = self._publisher
        if publisher is None:
            raise ConfigEventAggregateError(f"Publisher is not set in {self!r}")

        async with publisher.transaction() as context:
            for obj, kwargs in self._staged:
                await context.publish(obj, **kwargs)

        self._staged.clear()

    def cleanup(self):
        """
        Clears all staged events.
        """
        self._staged.clear()

    def enqueue(self, obj: Any, **kwargs):
        """
        Stages given event object with optional extra arguments.
        :param obj: event object
        :param kwargs: optional extra arguments
        """
        self._staged.append((obj, kwargs))
