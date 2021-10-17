from typing import Callable, Sequence

import pytest

from mediator.common.registry import (
    CollectionHandlerStore,
    CollisionHandlerStoreError,
    HandlerEntry,
    LookupHandlerStoreError,
    MappingHandlerStore,
    ModifierHandlerStore,
)
from mediator.common.registry.test.conftest import MockupHandler
from mediator.common.test.test_modifiers import MockupModifierFactory
from mediator.common.types import ActionSubject


@pytest.fixture
def first_part():
    return [
        HandlerEntry(handler=MockupHandler(str)),
        HandlerEntry(handler=MockupHandler(int)),
    ]


@pytest.fixture
def second_part():
    return [
        HandlerEntry(handler=MockupHandler(float)),
        HandlerEntry(handler=MockupHandler(bool)),
    ]


@pytest.fixture
def all_entries(
    first_part: Sequence[HandlerEntry], second_part: Sequence[HandlerEntry]
):
    return [
        *first_part,
        *second_part,
    ]


def test_collection_handler_store(
    first_part: Sequence[HandlerEntry],
    second_part: Sequence[HandlerEntry],
    all_entries: Sequence[HandlerEntry],
):
    store = CollectionHandlerStore()
    for entry in first_part:
        store.add(entry)
    store.include(second_part)
    store_entries = [*store]
    assert len(store_entries) == len(all_entries)
    assert {e.handler for e in all_entries} == {e.handler for e in store}


def test_mapping_handler_store(
    first_part: Sequence[HandlerEntry],
    second_part: Sequence[HandlerEntry],
    all_entries: Sequence[HandlerEntry],
):
    store = MappingHandlerStore()
    for entry in first_part:
        store.add(entry)
    store.include(second_part)
    assert {e.handler for e in all_entries} == {e.handler for e in store}

    with pytest.raises(CollisionHandlerStoreError):
        store.add(first_part[0])

    found = store.get(int)
    assert found.key == int
    assert found.handler == first_part[1].handler

    with pytest.raises(LookupHandlerStoreError):
        store.get(bytes)


@pytest.mark.asyncio
async def test_modifier_handler_store(
    mockup_action_factory: Callable[[], ActionSubject]
):
    entry_modifiers = MockupModifierFactory.modifiers("xyz")
    entry = HandlerEntry(
        handler=MockupHandler(str),
        modifiers=entry_modifiers,
    )

    nested_store = CollectionHandlerStore()
    assert ModifierHandlerStore.wrap(nested_store, ()) == nested_store

    store_modifiers = MockupModifierFactory.modifiers("abc")
    store = ModifierHandlerStore.wrap(nested_store, modifiers=store_modifiers)
    assert store != nested_store
    store.add(entry)
    store.include([entry])
    store_entries = [*store]
    assert len(store_entries) == 2
    for store_entry in store_entries:
        assert store_entry.handler == entry.handler
        call = store_entry.handler_pipeline()
        result = await call(mockup_action_factory())
        assert result.result == ("test", {"seq": list("abcxyz")})
