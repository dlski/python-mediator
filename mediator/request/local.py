from typing import Any, Dict, Hashable, Iterable, Optional, Sequence

from mediator.common.factory import (
    CallableHandlerPolicy,
    HandlerFactoryCascade,
    PolicyType,
)
from mediator.common.operators import OperatorDef
from mediator.common.registry import (
    HandlerEntry,
    HandlerRegistry,
    LookupHandlerStoreError,
    MapHandlerStore,
)
from mediator.common.types import ActionCallType, ActionResult, ActionSubject
from mediator.request.base import RequestExecutor


class _RequestExecutorHandlerStore(MapHandlerStore):
    _calls: Dict[Hashable, ActionCallType]

    def __init__(self):
        super().__init__()
        self._calls = {}

    def add(self, entry: HandlerEntry):
        super().add(entry)
        self._map_call(entry)

    def include(self, entries: Iterable[HandlerEntry]):
        super().include(entries)
        for entry in entries:
            self._map_call(entry)

    def _map_call(self, entry: HandlerEntry):
        self._calls[entry.key] = entry.handler_pipeline()

    async def __call__(self, action: ActionSubject) -> ActionResult:
        key = action.key
        call = self._calls.get(key)
        if call is None:
            raise LookupHandlerStoreError(f"Handler not defined for key {key}")
        return await call(action)


class LocalRequestBus(HandlerRegistry, RequestExecutor):
    def __init__(
        self,
        policies: Optional[Sequence[PolicyType]] = None,
        cascade: Optional[HandlerFactoryCascade] = None,
        operators: Sequence[OperatorDef] = (),
    ):
        executor_store = _RequestExecutorHandlerStore()
        HandlerRegistry.__init__(
            self,
            store=executor_store,
            policies=policies or [CallableHandlerPolicy()],
            cascade=cascade,
            operators=operators,
        )
        self._executor = executor_store

    async def execute(self, obj: Any, **kwargs):
        result = await self._executor(ActionSubject(subject=obj, inject=kwargs))
        assert isinstance(
            result, ActionResult
        ), "operator or handler should provide `ActionResult` type object"
        return result.result
