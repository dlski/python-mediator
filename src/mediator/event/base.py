from collections.abc import Iterable, Iterator
from contextlib import AbstractAsyncContextManager, nullcontext
from typing import Any, Protocol

from mediator.common.registry import HandlerEntry, HandlerStore


class EventPublish(Protocol):
    """
    Event publishing interface.
    """

    async def publish(self, obj: Any, **kwargs: Any) -> None:
        """
        Publishes given event object.
        :param obj: event object to be published
        :param kwargs: extra event arguments
        """
        ...


class EventPublisher(EventPublish, Protocol):
    """
    Event publisher interface, supporting transactions.
    """

    def transaction(self) -> AbstractAsyncContextManager[EventPublish]:
        """
        Provides transaction context manager returning event publish interface,
        to publish events inside of transaction.

        Classes that explicitly inherit from this protocol get default behaviour:
        no transaction, events are published directly by this publisher.
        :return: async context manager returning event publish interface
        """
        return nullcontext(self)


class EventSubscriber(HandlerStore, Protocol):
    """
    Event subscriber
    """

    def add(self, entry: HandlerEntry) -> None:
        """
        Connects handler entry to process events.
        :param entry: handler entry to connect
        """
        ...

    def include(self, entries: Iterable[HandlerEntry]) -> None:
        """
        Connects all handler entries from given iterable to process events.
        :param entries: handler entries iterator
        """
        ...

    def __iter__(self) -> Iterator[HandlerEntry]:
        """
        Returns iterator providing all underlying handler entries.
        :return: iterator providing all underlying handler entries.
        """
        ...
