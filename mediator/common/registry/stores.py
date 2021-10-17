from typing import Dict, Hashable, Iterable, Iterator, List, Sequence

from mediator.common.modifiers import ModifierFactory
from mediator.common.registry.base import (
    CollisionHandlerStoreError,
    HandlerEntry,
    HandlerStore,
    LookupHandlerStoreError,
)


class CollectionHandlerStore(HandlerStore):
    """
    Collection handler store.

    Ordinary handler store that holds handler entries in collection
    without any constraints.
    """

    def __init__(self):
        """
        Initializes collection handler store
        """
        self._entries: List[HandlerEntry] = []

    def add(self, entry: HandlerEntry):
        """
        Adds given handler entry into store.
        :param entry: handler entry to add into store
        """
        self._entries.append(entry)

    def include(self, entries: Iterable[HandlerEntry]):
        """
        Adds all handler entries from given iterable into store.
        :param entries: handler entries iterator
        """
        self._entries.extend(entries)

    def __iter__(self) -> Iterator[HandlerEntry]:
        """
        Returns iterator providing all underlying store handler entries.
        :return: iterator providing all underlying store handler entries.
        """
        return iter(self._entries)


class MappingHandlerStore(HandlerStore):
    """
    Mapping handler store.

    Handler store that stores entries in mapping
    and preserves uniqueness of stored entries by its keys.
    """

    def __init__(self):
        """
        Initializes mapping handler store
        """
        self._map: Dict[Hashable, HandlerEntry] = {}

    def add(self, entry: HandlerEntry):
        """
        Adds given handler entry into store.
        :param entry: handler entry to add into store
        :raises CollisionHandlerStoreError:
        when handler entry with given key already exists in this store
        """
        key = entry.key
        if key in self._map:
            raise CollisionHandlerStoreError(
                f"Handler entry with key {key} already exists"
            )
        self._map[entry.key] = entry

    def include(self, entries: Iterable[HandlerEntry]):
        """
        Adds all handler entries from given iterable into store.
        :param entries: handler entries iterator
        :raises CollisionHandlerStoreError:
        when handler entry with given key already exists in this store
        """
        for entry in entries:
            self.add(entry)

    def __iter__(self) -> Iterator[HandlerEntry]:
        """
        Returns iterator providing all underlying store handler entries.
        :return: iterator providing all underlying store handler entries.
        """
        return iter(self._map.values())

    def get(self, key: Hashable) -> HandlerEntry:
        """
        Returns handler entry with matching key.
        :param key: key to find matching handler entry
        :raises LookupHandlerStoreError: when there is no handler entry with given key
        :return: handler entry with matching key
        """
        if key not in self._map:
            raise LookupHandlerStoreError(f"Handler entry for key {key} not found")
        return self._map[key]


class ModifierHandlerStore(HandlerStore):
    """
    Modifier handler store.

    Handler store that for every new entry adds its modifiers stack
    and adds modified entries into underlying handler store.
    """

    def __init__(self, nested: HandlerStore, modifiers: Sequence[ModifierFactory]):
        """
        Initializes modifier handler store.
        :param nested: handler store used for modified entries storage
        :param modifiers: modifiers to be applied on every new handler entry
        """
        self._nested = nested
        self._modifiers = tuple(modifiers)

    def add(self, entry: HandlerEntry):
        """
        Adds given handler entry into store.
        :param entry: handler entry to add into store
        """
        self._nested.add(entry.stack(self._modifiers))

    def include(self, entries: Iterable[HandlerEntry]):
        """
        Adds all handler entries from given iterable into store.
        :param entries: handler entries iterator
        """
        for entry in entries:
            self.add(entry)

    def __iter__(self) -> Iterator[HandlerEntry]:
        """
        Returns iterator providing all underlying store handler entries.
        :return: iterator providing all underlying store handler entries.
        """
        return iter(self._nested)

    @classmethod
    def wrap(
        cls, nested: HandlerStore, modifiers: Sequence[ModifierFactory]
    ) -> HandlerStore:
        """
        Wraps given handler store into modifier handler store if any modifiers provided
        or returns unchanged if there are no modifiers.
        :param nested: handler store to be nested into  modifier handler store
        :param modifiers: sequence of modifiers to apply on every new store entry
        :return: handler store with entry modifier stack apply
        """
        if modifiers:
            return cls(nested=nested, modifiers=modifiers)
        return nested
