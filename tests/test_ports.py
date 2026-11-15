"""
Checks that library ports are structural:
objects satisfy them by shape, without inheriting from library classes.
"""

from collections.abc import Hashable
from contextlib import AbstractAsyncContextManager, nullcontext
from typing import Any

import pytest

from mediator.common.handler import Handler
from mediator.common.modifiers import ModifierFactory, ModifierStack
from mediator.common.registry import HandlerStore
from mediator.common.types import ActionCallType, ActionResult, ActionSubject
from mediator.event import (
    EventAggregate,
    EventPublish,
    EventPublisher,
    EventSubscriber,
    LocalEventBus,
)
from mediator.request import LocalRequestBus, RequestExecutor


class _PlainHandler:
    @property
    def key(self) -> Hashable:
        return str

    @property
    def obj(self) -> Any:
        return self

    async def __call__(self, action: ActionSubject) -> ActionResult:
        return ActionResult(action.subject)


class _PlainPublisher:
    def __init__(self) -> None:
        self.published: list[Any] = []

    def transaction(self) -> AbstractAsyncContextManager[EventPublish]:
        return nullcontext(self)

    async def publish(self, obj: Any, **kwargs: Any) -> None:
        self.published.append(obj)


class _TargetModifier:
    def __init__(self) -> None:
        self.targets: list[ActionCallType] = []

    def create(self, call: ActionCallType, *, target: ActionCallType) -> ActionCallType:
        self.targets.append(target)
        return call


def test_local_buses_satisfy_ports() -> None:
    event_bus = LocalEventBus()
    publisher: EventPublisher = event_bus
    subscriber: EventSubscriber = event_bus
    store: HandlerStore = event_bus
    executor: RequestExecutor = LocalRequestBus()
    assert all(port is not None for port in (publisher, subscriber, store, executor))


def test_handler_is_runtime_checkable() -> None:
    assert isinstance(_PlainHandler(), Handler)
    assert not isinstance(object(), Handler)


@pytest.mark.asyncio
async def test_plain_publisher_with_aggregate() -> None:
    publisher = _PlainPublisher()
    aggregate = EventAggregate().use(publisher)
    aggregate.enqueue("event")
    await aggregate.commit()
    assert publisher.published == ["event"]


@pytest.mark.asyncio
async def test_plain_modifier_receives_target() -> None:
    handler = _PlainHandler()
    modifier = _TargetModifier()
    factories: list[ModifierFactory] = [modifier, modifier]
    call = ModifierStack.build(factories, handler)
    result = await call(ActionSubject(subject="test", inject={}))
    assert result.result == "test"
    assert modifier.targets == [handler, handler]
