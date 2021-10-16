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
    await bus.publish(MessageEvent(message="test"))
    # -- output --
    # first handler: test
    # second handler: test
