from typing import Dict, Hashable, Iterable, List, Sequence

from mediator.common.operators import OperatorDef
from mediator.common.registry.base import (
    CollisionHandlerStoreError,
    HandlerEntry,
    HandlerStore,
    LookupHandlerStoreError,
)


class CollectionHandlerStore(HandlerStore):
    def __init__(self):
        self._entries: List[HandlerEntry] = []

    def add(self, entry: HandlerEntry):
        self._entries.append(entry)

    def include(self, entries: Iterable[HandlerEntry]):
        self._entries.extend(entries)

    def __iter__(self) -> Iterable[HandlerEntry]:
        return iter(self._entries)


class MapHandlerStore(HandlerStore):
    def __init__(self):
        self._map: Dict[Hashable, HandlerEntry] = {}

    def add(self, entry: HandlerEntry):
        key = entry.key
        if key in self._map:
            raise CollisionHandlerStoreError(
                f"Handler entry with key {key} already exists"
            )
        self._map[entry.key] = entry

    def include(self, entries: Iterable[HandlerEntry]):
        for entry in entries:
            self.add(entry)

    def __iter__(self) -> Iterable[HandlerEntry]:
        return iter(self._map.values())

    def get(self, key: Hashable) -> HandlerEntry:
        if key not in self._map:
            raise LookupHandlerStoreError(f"Handler entry for key {key} not found")
        return self._map[key]


class OperatorHandlerStore(HandlerStore):
    def __init__(self, nested: HandlerStore, operators: Sequence[OperatorDef]):
        self._nested = nested
        self._operators = tuple(operators)

    def add(self, entry: HandlerEntry):
        self._nested.add(entry.stack(self._operators))

    def include(self, entries: Iterable[HandlerEntry]):
        for entry in entries:
            self.add(entry)

    def __iter__(self) -> Iterable[HandlerEntry]:
        return iter(self._nested)

    @classmethod
    def wrap(cls, nested: HandlerStore, operators: Sequence[OperatorDef]):
        if operators:
            return cls(nested=nested, operators=operators)
        return nested
