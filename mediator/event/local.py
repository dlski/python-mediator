import asyncio
from collections import defaultdict
from typing import Any, Dict, Hashable, Iterable, List, Optional, Sequence

from mediator.common.factory import (
    CallableHandlerPolicy,
    HandlerFactoryCascade,
    PolicyType,
)
from mediator.common.operators import OperatorDef
from mediator.common.registry import (
    CollectionHandlerStore,
    HandlerEntry,
    HandlerRegistry,
)
from mediator.common.types import ActionCallType, ActionSubject
from mediator.event.base import EventPublisher, EventSubscriber


class _EventSchedulerHandlerStore(CollectionHandlerStore):
    _groups: Dict[Hashable, List[ActionCallType]]

    def __init__(self, sync_mode: bool = False):
        super().__init__()
        self._groups = defaultdict(list)
        self.sync_mode = sync_mode

    def add(self, entry: HandlerEntry):
        super().add(entry)
        self._map_call(entry)

    def include(self, entries: Iterable[HandlerEntry]):
        super().include(entries)
        for entry in entries:
            self._map_call(entry)

    def _map_call(self, entry: HandlerEntry):
        self._groups[entry.key].append(entry.handler_pipeline())

    async def schedule(self, action: ActionSubject):
        key = action.key
        group: List[ActionCallType] = self._groups.get(key, ())
        tasks = [asyncio.create_task(call(action)) for call in group]
        if self.sync_mode:
            await asyncio.wait(tasks)


class LocalEventBus(EventPublisher, HandlerRegistry, EventSubscriber):
    def __init__(
        self,
        policies: Optional[Sequence[PolicyType]] = None,
        cascade: Optional[HandlerFactoryCascade] = None,
        operators: Sequence[OperatorDef] = (),
        sync_mode: bool = False,
    ):
        scheduler_store = _EventSchedulerHandlerStore(sync_mode=sync_mode)
        HandlerRegistry.__init__(
            self,
            store=scheduler_store,
            policies=policies or [CallableHandlerPolicy()],
            cascade=cascade,
            operators=operators,
        )
        self._scheduler = scheduler_store

    async def publish(self, obj: Any, **kwargs):
        await self._scheduler.schedule(ActionSubject(subject=obj, inject=kwargs))
