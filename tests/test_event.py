import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncContextManager, Mapping, Type

import pytest

from mediator.common.factory import CallableHandlerPolicy
from mediator.event import (
    ConfigEventAggregateError,
    EventAggregate,
    EventHandlerRegistry,
    EventPublisher,
    LocalEventBus,
)


@dataclass
class _MockupEvent:
    to_set: Mapping[int, asyncio.Event]


@dataclass
class _MockupEvent1(_MockupEvent):
    pass


@dataclass
class _MockupEvent2(_MockupEvent):
    pass


def _create_event_handler(index: int, type_: Type):
    async def _event_handler(event: type_):
        event.to_set[index].set()

    return _event_handler


@pytest.mark.asyncio
async def test_local_event_bus():
    policies = [CallableHandlerPolicy()]
    bus = LocalEventBus(policies=policies)
    registry = EventHandlerRegistry(policies=policies)

    bus.register(_create_event_handler(0, _MockupEvent1))
    bus.register(_create_event_handler(1, _MockupEvent1))
    registry.register(_create_event_handler(100, _MockupEvent2))
    registry.register(_create_event_handler(200, _MockupEvent2))
    bus.include(registry)

    events = {i: asyncio.Event() for i in [0, 1, 100, 200]}

    for seq, event_type in [
        ([0, 1], _MockupEvent1),
        ([100, 200], _MockupEvent2),
    ]:
        await bus.publish(event_type(to_set=events))
        for i in seq:
            event = events[i]
            await asyncio.wait_for(event.wait(), timeout=0.5)


class _MockupEventPublisher(EventPublisher):
    def __init__(self):
        self.calls = []

    async def publish(self, obj: Any, **kwargs):
        self.calls.append((obj, kwargs))

    def clear(self):
        self.calls.clear()


class _ExpectMockupEventPublisher(_MockupEventPublisher):
    def __init__(self, expected_calls):
        super().__init__()
        self.expected_calls = expected_calls

    @asynccontextmanager
    async def transaction(self) -> AsyncContextManager:
        nested_publisher = _MockupEventPublisher()
        before_calls = list(self.calls)
        yield nested_publisher
        assert nested_publisher.calls == self.expected_calls
        assert self.calls == before_calls
        self.calls.extend(nested_publisher.calls)


@dataclass
class _MockupAggregateEvent1:
    value: int


@dataclass
class _MockupAggregateEvent2:
    value: str


class _MockupAggregate(EventAggregate):
    def add_event1(self, value: int):
        self._enqueue(_MockupAggregateEvent1(value))

    def add_event2(self, value: str):
        self._enqueue(_MockupAggregateEvent2(value), test="test")


@pytest.mark.asyncio
async def test_event_aggregate():
    aggregate = _MockupAggregate()

    with pytest.raises(ConfigEventAggregateError):
        await aggregate.commit()

    aggregate.use(
        _ExpectMockupEventPublisher(
            [
                (_MockupAggregateEvent1(1), {}),
                (_MockupAggregateEvent1(2), {}),
                (_MockupAggregateEvent2("event"), {"test": "test"}),
            ]
        )
    )
    aggregate.add_event1(1)
    aggregate.add_event1(2)
    aggregate.add_event2("event")
    await aggregate.commit()

    publisher = _MockupEventPublisher()
    aggregate.use(publisher)
    await aggregate.commit()
    assert publisher.calls == []

    aggregate.add_event2("test")
    aggregate.cleanup()
    await aggregate.commit()
    assert publisher.calls == []
