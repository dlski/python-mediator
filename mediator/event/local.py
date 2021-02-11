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

    def __init__(self):
        super().__init__()
        self._groups = defaultdict(list)

    def add(self, entry: HandlerEntry):
        super().add(entry)
        self._map_call(entry)

    def include(self, entries: Iterable[HandlerEntry]):
        super().include(entries)
        for entry in entries:
            self._map_call(entry)

    def _map_call(self, entry: HandlerEntry):
        self._groups[entry.key].append(entry.handler_pipeline())

    def schedule(self, action: ActionSubject):
        key = action.key
        group: List[ActionCallType] = self._groups.get(key, ())
        for call in group:
            asyncio.create_task(call(action))


class LocalEventBus(EventPublisher, HandlerRegistry, EventSubscriber):
    def __init__(
        self,
        policies: Optional[Sequence[PolicyType]] = None,
        cascade: Optional[HandlerFactoryCascade] = None,
        operators: Sequence[OperatorDef] = (),
    ):
        executor_store = _EventSchedulerHandlerStore()
        HandlerRegistry.__init__(
            self,
            store=executor_store,
            policies=policies or [CallableHandlerPolicy()],
            cascade=cascade,
            operators=operators,
        )
        self._executor = executor_store

    async def publish(self, obj: Any, **kwargs):
        self._executor.schedule(ActionSubject(subject=obj, inject=kwargs))
