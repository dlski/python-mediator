from typing import Any, AsyncContextManager, Iterable, Iterator

from mediator.common.registry import HandlerEntry, HandlerStore
from mediator.utils.context import AsyncNullContextManager


class EventPublish:
    """
    Event publishing interface.
    """

    async def publish(self, obj: Any, **kwargs):
        """
        Publishes given event object.
        :param obj: event object to be published
        :param kwargs: extra event arguments
        """
        raise NotImplementedError


class EventPublisher(EventPublish):
    """
    Event publisher interface, supporting transactions.
    """

    # noinspection PyMethodMayBeStatic
    def transaction(self) -> AsyncContextManager[EventPublish]:
        """
        Provides transaction context manager returning event publish interface,
        to publish events inside of transaction.
        :return: async context manager returning event publish interface
        """
        return AsyncNullContextManager(self)

    async def publish(self, obj: Any, **kwargs):
        """
        Publishes given event object.
        :param obj: event object to be published
        :param kwargs: extra event arguments
        """
        raise NotImplementedError


class EventSubscriber(HandlerStore):
    """
    Event subscriber
    """

    def add(self, entry: HandlerEntry):
        """
        Connects handler entry to process events.
        :param entry: handler entry to connect
        """
        raise NotImplementedError

    def include(self, entries: Iterable[HandlerEntry]):
        """
        Connects all handler entries from given iterable to process events.
        :param entries: handler entries iterator
        """
        raise NotImplementedError

    def __iter__(self) -> Iterator[HandlerEntry]:
        """
        Returns iterator providing all underlying handler entries.
        :return: iterator providing all underlying handler entries.
        """
        raise NotImplementedError
