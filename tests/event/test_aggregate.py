from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

import pytest

from mediator.event import ConfigEventAggregateError, EventAggregate, EventPublisher


class _MockupEventPublisher(EventPublisher):
    def __init__(self):
        self.calls = []

    async def publish(self, obj: Any, **kwargs):
        self.calls.append((obj, kwargs))

    def clear(self):
        self.calls.clear()


@dataclass
class _Event1:
    value: int


@dataclass
class _Event2:
    value: str


class _MockupAggregate(EventAggregate):
    def add_event1(self, value: int):
        self.enqueue(_Event1(value))

    def add_event2(self, value: str):
        self.enqueue(_Event2(value), test="test")


@pytest.mark.asyncio
async def test_event_aggregate():
    aggregate = _MockupAggregate()

    with pytest.raises(ConfigEventAggregateError):
        await aggregate.commit()

    publisher = _MockupEventPublisher()
    aggregate.use(publisher)
    await aggregate.commit()
    assert publisher.calls == []

    aggregate.add_event2("test")
    aggregate.cleanup()
    await aggregate.commit()
    assert publisher.calls == []


class _ExpectMockupEventPublisher(_MockupEventPublisher):
    def __init__(self, expected_calls):
        super().__init__()
        self.expected_calls = expected_calls

    @asynccontextmanager
    async def transaction(self):
        nested_publisher = _MockupEventPublisher()
        before_calls = list(self.calls)
        yield nested_publisher
        assert nested_publisher.calls == self.expected_calls
        assert self.calls == before_calls
        self.calls.extend(nested_publisher.calls)


@pytest.mark.asyncio
async def test_event_aggregate_transaction():
    aggregate = _MockupAggregate()
    aggregate.use(
        _ExpectMockupEventPublisher(
            [
                (_Event1(1), {}),
                (_Event1(2), {}),
                (_Event2("event"), {"test": "test"}),
            ]
        )
    )
    aggregate.add_event1(1)
    aggregate.add_event1(2)
    aggregate.add_event2("event")
    await aggregate.commit()
