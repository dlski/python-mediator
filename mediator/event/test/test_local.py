import asyncio
from typing import Mapping, Type

import pytest

from mediator.common.factory import CallableHandlerPolicy
from mediator.event import EventHandlerRegistry, LocalEventBus


class _MockupEvent1:
    pass


class _MockupEvent2:
    pass


def _create_event_handler(events: Mapping[int, asyncio.Event], index: int, type_: Type):
    async def _event_handler(_: type_):  # type: ignore
        await asyncio.sleep(0.0)
        events[index].set()

    return _event_handler


@pytest.mark.asyncio
async def test_local_event_bus():
    policies = [CallableHandlerPolicy()]
    bus = LocalEventBus(policies=policies)
    registry = EventHandlerRegistry(policies=policies)

    events = {i: asyncio.Event() for i in [0, 1, 100, 200]}

    bus.register(_create_event_handler(events, 0, _MockupEvent1))
    bus.register(_create_event_handler(events, 1, _MockupEvent1))
    registry.register(_create_event_handler(events, 100, _MockupEvent2))
    registry.register(_create_event_handler(events, 200, _MockupEvent2))
    bus.include(registry)

    for to_check, event_type in [
        ([0, 1], _MockupEvent1),
        ([100, 200], _MockupEvent2),
    ]:
        await bus.publish(event_type())
        for index in to_check:
            event = events[index]
            await asyncio.wait_for(event.wait(), timeout=0.5)


@pytest.mark.asyncio
async def test_local_event_bus_sync():
    cnt = {"test": 0}

    async def _handler(event: str):
        await asyncio.sleep(0.0)
        cnt[event] += 1

    policies = [CallableHandlerPolicy()]
    bus = LocalEventBus(policies=policies, sync_mode=True)
    bus.register(_handler, policies=policies)
    bus.register(_handler, policies=policies)
    await bus.publish("test")
    assert cnt["test"] == 2
