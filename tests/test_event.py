import asyncio
from dataclasses import dataclass
from typing import Mapping, Type

import pytest

from mediator.common.factory import CallableHandlerPolicy
from mediator.event import EventHandlerRegistry, LocalEventBus


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
