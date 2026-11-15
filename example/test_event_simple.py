from dataclasses import dataclass

import pytest

from mediator.event import LocalEventBus

bus = LocalEventBus()


@dataclass
class MessageEvent:
    message: str


@bus.register
async def first_handler(event: MessageEvent):
    print(f"first handler: {event.message}")


@bus.register
async def second_handler(event: MessageEvent):
    print(f"second handler: {event.message}")


@pytest.mark.asyncio
async def test_event_simple():
    # handlers run in background, publishing does not wait for them
    await bus.publish(MessageEvent(message="test"))
    # wait until all handlers are finished (i.e. on application shutdown)
    await bus.drain()
    # -- output --
    # first handler: test
    # second handler: test
