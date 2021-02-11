import functools
from typing import Any, Iterable, Optional, Sequence

from mediator.common.factory.cascade import HandlerFactoryCascade
from mediator.common.factory.policies import PolicyType
from mediator.common.operators import OperatorDef
from mediator.common.registry.base import HandlerEntry, HandlerStore
from mediator.common.registry.stores import OperatorHandlerStore


class AbstractHandlerRegistry(HandlerStore):
    def __init__(
        self,
        policies: Optional[Sequence[PolicyType]] = None,
        cascade: Optional[HandlerFactoryCascade] = None,
    ):
        self._cascade = self._provide_cascade(policies=policies, cascade=cascade)

    @classmethod
    def _provide_cascade(
        cls,
        policies: Optional[Sequence[PolicyType]],
        cascade: Optional[HandlerFactoryCascade],
    ):
        if cascade is not None:
            return cascade
        if policies is not None:
            return HandlerFactoryCascade(policies=policies)
        raise TypeError("policies and cascade are not defined")

    def register(
        self,
        obj: Optional[Any] = None,
        *,
        policies: Optional[Sequence[PolicyType]] = None,
        operators: Sequence[OperatorDef] = (),
    ):
        cascade = self._policies_cascade(policies)
        if obj is None:
            process = functools.partial(
                self._process_obj, cascade=cascade, operators=operators
            )

            def wrap(fn: Any):
                process(fn)
                return fn

            return wrap

        else:
            self._process_obj(obj, cascade=cascade, operators=operators)
            return obj

    def _policies_cascade(
        self, policies: Optional[Sequence[PolicyType]]
    ) -> HandlerFactoryCascade:
        if policies is None:
            return self._cascade
        else:
            return self._cascade.replace(policies)

    def _process_obj(
        self,
        obj: Any,
        *,
        cascade: HandlerFactoryCascade,
        operators: Sequence[OperatorDef],
    ):
        handler = cascade(obj)
        self.add(HandlerEntry(handler=handler, operators=operators))

    def add(self, entry: HandlerEntry):
        raise NotImplementedError

    def include(self, entries: Iterable[HandlerEntry]):
        raise NotImplementedError

    def __iter__(self) -> Iterable[HandlerEntry]:
        raise NotImplementedError


class HandlerRegistry(AbstractHandlerRegistry):
    def __init__(
        self,
        store: HandlerStore,
        policies: Optional[Sequence[PolicyType]] = None,
        cascade: Optional[HandlerFactoryCascade] = None,
        operators: Sequence[OperatorDef] = (),
    ):
        AbstractHandlerRegistry.__init__(self, policies=policies, cascade=cascade)
        self._store = OperatorHandlerStore.wrap(nested=store, operators=operators)

    def add(self, entry: HandlerEntry):
        self._store.add(entry)

    def include(self, entries: Iterable[HandlerEntry]):
        self._store.include(entries)

    def __iter__(self) -> Iterable[HandlerEntry]:
        return iter(self._store)
