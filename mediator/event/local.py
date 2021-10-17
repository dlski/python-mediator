import asyncio
from collections import defaultdict
from typing import Any, DefaultDict, Hashable, Iterable, List, Optional, Sequence

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
from mediator.event.base import EventPublisher, EventSubscriber


class _EventSchedulerHandlerStore(CollectionHandlerStore):
    """
    Utility event handler store, based on collection handler store
    to work with local event execution.
    Schedules event processing as background asyncio tasks.
    """

    _groups: DefaultDict[Hashable, List[ActionCallType]]

    def __init__(self, sync_mode: bool = False):
        """
        Initializes event scheduler handler store.
        :param sync_mode: are events should be processed in background
        when True every schedule call waits on event processing to finish
        when False (default) event processing is executed in background;
        useful in test cases
        """
        super().__init__()
        self._groups = defaultdict(list)
        self.sync_mode = sync_mode

    def add(self, entry: HandlerEntry):
        """
        Adds given handler entry into store
        and connects handler entry to process events.
        :param entry: handler entry to connect
        """
        super().add(entry)
        self._map_call(entry)

    def include(self, entries: Iterable[HandlerEntry]):
        """
        Adds all handler entries from given iterable into store
        and connects all handler entries from given iterable to process events.
        :param entries: handler entries iterator
        """
        super().include(entries)
        for entry in entries:
            self._map_call(entry)

    def _map_call(self, entry: HandlerEntry):
        """
        Add given handler entry to event processing.
        :param entry: handler entry to add
        """
        self._groups[entry.key].append(entry.handler_pipeline())

    async def schedule(self, action: ActionSubject):
        """
        Schedule given action object to be processed as event
        by all collected handlers.
        :param action: event action to be processed
        """
        key = action.key
        group: Sequence[ActionCallType] = self._groups.get(key, ())
        tasks = [asyncio.create_task(call(action)) for call in group]
        if self.sync_mode:
            await asyncio.wait(tasks)


class LocalEventBus(EventPublisher, HandlerRegistry, EventSubscriber):
    """
    Local event bus.

    Performs event execution scheduling locally in-place as asyncio backgrount tasks.
    Connects behaviours of handler registry and event publisher interface.
    """

    def __init__(
        self,
        policies: Optional[Sequence[PolicyType]] = None,
        cascade: Optional[HandlerFactoryCascade] = None,
        modifiers: Sequence[ModifierFactory] = (),
        sync_mode: bool = False,
    ):
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
        """
        scheduler_store = _EventSchedulerHandlerStore(sync_mode=sync_mode)
        HandlerRegistry.__init__(
            self,
            store=scheduler_store,
            policies=policies or [CallableHandlerPolicy()],
            cascade=cascade,
            modifiers=modifiers,
        )
        self._scheduler = scheduler_store

    async def publish(self, obj: Any, **kwargs):
        """
        Publishes given event.
        :param obj: event object
        :param kwargs: event extra arguments
        """
        await self._scheduler.schedule(ActionSubject(subject=obj, inject=kwargs))
