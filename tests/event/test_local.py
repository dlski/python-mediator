import asyncio
import logging
from collections.abc import Mapping

import pytest

from mediator.common.factory import CallableHandlerPolicy
from mediator.event import (
    AwaitingEventDispatcher,
    BackgroundEventDispatcher,
    EventHandlerRegistry,
    LocalEventBus,
)


class _MockupEvent1:
    pass


class _MockupEvent2:
    pass


def _create_event_handler(events: Mapping[int, asyncio.Event], index: int, type_: type):
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


class _HandlerError(Exception):
    pass


@pytest.mark.asyncio
async def test_local_event_bus_awaiting():
    cnt = {"test": 0}

    async def _handler(event: str):
        await asyncio.sleep(0.0)
        cnt[event] += 1

    bus = LocalEventBus(dispatcher=AwaitingEventDispatcher())
    bus.register(_handler)
    bus.register(_handler)
    await bus.publish("test")
    assert cnt["test"] == 2

    # nothing to wait for
    await bus.publish(object())
    await bus.drain()


@pytest.mark.asyncio
async def test_local_event_bus_awaiting_error():
    finished = []

    async def _failing(event: str):
        raise _HandlerError(event)

    async def _working(event: str):
        await asyncio.sleep(0.0)
        finished.append(event)

    bus = LocalEventBus(dispatcher=AwaitingEventDispatcher())
    bus.register(_failing)
    bus.register(_working)
    bus.register(_failing)

    with pytest.raises(ExceptionGroup) as e:
        await bus.publish("test")
    assert [type(error) for error in e.value.exceptions] == [_HandlerError] * 2
    assert finished == ["test"]


@pytest.mark.asyncio
async def test_local_event_bus_background_drain():
    finished: list[object] = []
    bus = LocalEventBus()

    @bus.register
    async def _first(event: str):
        await asyncio.sleep(0.0)
        await bus.publish(len(event))
        finished.append(event)

    @bus.register
    async def _second(event: int):
        await asyncio.sleep(0.0)
        finished.append(event)

    await bus.publish("test")
    assert finished == []

    await bus.drain()
    assert finished == ["test", 4]
    await bus.drain()


@pytest.mark.asyncio
async def test_local_event_bus_background_error():
    errors = []
    bus = LocalEventBus(
        dispatcher=BackgroundEventDispatcher(
            on_error=lambda action, error: errors.append((action.subject, error))
        )
    )

    @bus.register
    async def _failing(event: str):
        raise _HandlerError(event)

    await bus.publish("test")
    await bus.drain()
    [(subject, error)] = errors
    assert subject == "test"
    assert isinstance(error, _HandlerError)


@pytest.mark.asyncio
async def test_local_event_bus_background_error_log(caplog: pytest.LogCaptureFixture):
    bus = LocalEventBus()

    @bus.register
    async def _failing(event: str):
        raise _HandlerError(event)

    with caplog.at_level(logging.ERROR, logger="mediator.event.dispatch"):
        await bus.publish("test")
        await bus.drain()
    [record] = caplog.records
    assert "Event str handler failed" in record.getMessage()
    assert record.exc_info is not None
    assert isinstance(record.exc_info[1], _HandlerError)


@pytest.mark.asyncio
async def test_local_event_bus_include_iterator():
    handled = []
    registry = EventHandlerRegistry()

    @registry.register
    async def _handler(event: str):
        handled.append(event)

    bus = LocalEventBus(dispatcher=AwaitingEventDispatcher())
    bus.include(iter(registry))
    assert len(list(bus)) == 1

    await bus.publish("test")
    assert handled == ["test"]
