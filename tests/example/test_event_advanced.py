from dataclasses import dataclass

import pytest

from mediator.common.factory import CallableHandlerPolicy, MethodHandlerPolicy
from mediator.event import EventHandlerRegistry, LocalEventBus

# Create local event registry with given policies.
# Single policy tells the handler inspector where to find callable
# which handles particular action.
# - add policy that suggest to get object attribute named "handle"
#   and try to analyze as event handler
# - add policy that suggest given object is event handler callable
registry = EventHandlerRegistry(
    policies=[MethodHandlerPolicy(name="handle"), CallableHandlerPolicy()],
)


@dataclass
class MessageEvent:
    message: str


class MessageEventHandler:
    async def handle(self, event: MessageEvent):
        print(f"from object handler: {event.message}")


# ... MethodHandlerPolicy(...) gives ability to inspect handler object

handler = MessageEventHandler()
registry.register(handler)

# ... CallableHandlerPolicy(...) gives ability to inspect plain function


@registry.register
async def message_event_handler(some_event: MessageEvent):
    print(f"from function handler: {some_event.message}")


@pytest.mark.asyncio
async def test_event_advanced():
    # create local event bus and include handlers from registry
    bus = LocalEventBus()
    # registry usage is optional - used for example purposes,
    # LocalEventBus implements same registry interface
    bus.include(registry)

    # publish event
    await bus.publish(MessageEvent(message="test"))

    # output:
    #   from object handler: test
    #   from function handler: test
