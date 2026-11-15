from collections import defaultdict
from collections.abc import Hashable, Iterable, Sequence
from typing import Any

from mediator.common.factory import (
    CallableHandlerPolicy,
    HandlerFactoryCascade,
    PolicyType,
)
from mediator.common.modifiers import ModifierFactory
from mediator.common.registry import (
    CollectionHandlerStore,
    HandlerEntry,
    HandlerRegistry,
)
from mediator.common.types import ActionCallType, ActionSubject
from mediator.event.base import EventPublisher
from mediator.event.dispatch import BackgroundEventDispatcher, EventDispatcher


class _EventCallHandlerStore(CollectionHandlerStore):
    """
    Utility event handler store, based on collection handler store
    to work with local event execution.
    Keeps event handler calls grouped by event key.
    """

    def __init__(self) -> None:
        """
        Initializes empty event call handler store.
        """
        super().__init__()
        self._groups: defaultdict[Hashable, list[ActionCallType]] = defaultdict(list)

    def add(self, entry: HandlerEntry) -> None:
        """
        Adds given handler entry into store
        and connects handler entry to process events.
        :param entry: handler entry to connect
        """
        super().add(entry)
        self._groups[entry.key].append(entry.handler_pipeline())

    def include(self, entries: Iterable[HandlerEntry]) -> None:
        """
        Adds all handler entries from given iterable into store
        and connects all handler entries from given iterable to process events.
        :param entries: handler entries iterator
        """
        for entry in entries:
            self.add(entry)

    def calls(self, key: Hashable) -> Sequence[ActionCallType]:
        """
        Provides all event handler calls connected to given event key.
        :param key: event key
        :return: sequence of event handler calls (empty when nothing is connected)
        """
        return self._groups.get(key, ())


class LocalEventBus(HandlerRegistry, EventPublisher):
    """
    Local event bus.

    Runs event handlers locally in-place using event dispatcher
    (by default as asyncio background tasks).
    Connects behaviours of handler registry and event publisher interface.
    """

    def __init__(
        self,
        policies: Sequence[PolicyType] | None = None,
        cascade: HandlerFactoryCascade | None = None,
        modifiers: Sequence[ModifierFactory] = (),
        dispatcher: EventDispatcher | None = None,
    ) -> None:
        """
        Initializes local event bus with given specification.
        :param policies:
        (optional) sequence of policies to be used as recipe
        to convert raw objects into handlers;
        if not provided default `CallableHandlerPolicy` will be used;
        overwritten when cascade is provided
        :param cascade:
        (optional) custom handler factory cascade to customize
        policy into handler factory mapping
        :param modifiers: sequence of modifiers to be applied on new handler entries
        :param dispatcher:
        (optional) strategy that runs event handlers;
        by default `BackgroundEventDispatcher` is used
        (publishing does not wait for event handlers);
        use `AwaitingEventDispatcher` to wait for event handlers when publishing
        """
        store = _EventCallHandlerStore()
        super().__init__(
            store=store,
            policies=policies or [CallableHandlerPolicy()],
            cascade=cascade,
            modifiers=modifiers,
        )
        self._calls = store
        self._dispatcher = dispatcher or BackgroundEventDispatcher()

    async def publish(self, obj: Any, **kwargs: Any) -> None:
        """
        Publishes given event.
        :param obj: event object
        :param kwargs: event extra arguments
        """
        action = ActionSubject(subject=obj, inject=kwargs)
        await self._dispatcher.dispatch(self._calls.calls(action.key), action)

    async def drain(self) -> None:
        """
        Waits until all event handlers started by this bus are finished.
        Useful for graceful shutdown when events are processed in background.
        """
        await self._dispatcher.drain()
