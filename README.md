# python-mediator

[![CI](https://github.com/dlski/python-mediator/actions/workflows/ci.yml/badge.svg?branch=master&event=push)](https://github.com/dlski/python-mediator/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/dlski/python-mediator/branch/master/graph/badge.svg?token=AU4T4Z81F6)](https://codecov.io/gh/dlski/python-mediator)
[![pypi](https://img.shields.io/pypi/v/python-mediator.svg)](https://pypi.python.org/pypi/python-mediator)
[![downloads](https://img.shields.io/pypi/dm/python-mediator.svg)](https://pypistats.org/packages/python-mediator)
[![versions](https://img.shields.io/pypi/pyversions/python-mediator.svg)](https://pypi.python.org/pypi/python-mediator)
[![license](https://img.shields.io/github/license/dlski/python-mediator.svg)](https://github.com/dlski/python-mediator/blob/master/LICENSE)

Elastic and extensible high-performance asyncio CQRS + ES python microframework.
Compatible with Python 3.11+ (CPython and PyPy).

Corresponds to clean architecture patterns, ideal for
command/query segregation scenarios and event-driven design approaches.

Key features:
- **automatic handler inspection and action matching** -
  like in modern frameworks (FastAPI, Typer, Click etc.) machinery is fully automatic
  and command, query or event object is matched with handler automatically
- **extra parameters injection with ease** -
  extra context information like credentials can be passed safely and easily to handler
  with zero complexity
- **configurable middleware (modifier) stack** -
  handler call flow can be extended easily
  with i.e. data mapping, special exception handling or extra logging
  by defining modifier stack that wraps handler execution
- **fully typed** -
  ships type information, interfaces are `typing.Protocol` classes,
  so application code does not have to inherit from library classes
- **ultra-lightweight and performance optimized** -
  has no external dependencies and all features are implemented
  in care of low runtime overhead

## Installation
```shell
pip install python-mediator
# or
uv add python-mediator
```

## A command/query handling example
```python
from dataclasses import dataclass

from mediator import LocalRequestBus, Request

bus = LocalRequestBus()


@dataclass
class PrintMessageCommand:
    message: str


@bus.register
async def command_handler(event: PrintMessageCommand):
    print(f"print message: {event.message}")
    return event.message


# Request base class is optional: it tells type checker
# what is the result type of request execution
@dataclass
class DataQuery(Request[dict[str, object]]):
    id: int


@bus.register
async def query_handler(query: DataQuery) -> dict[str, object]:
    print(f"data query: {query.id}")
    return {"id": query.id, "data": "test"}


async def main():
    printed_message = await bus.execute(PrintMessageCommand(message="test"))
    assert printed_message == "test"

    data = await bus.execute(DataQuery(id=1))  # type checker knows: dict[str, object]
    assert data == {"id": 1, "data": "test"}

    # -- output --
    # print message: test
    # data query: 1
```
Every request type has exactly one handler.
More advanced example available in [example/test_request_advanced.py](example/test_request_advanced.py) for reference.

## An event handling example
```python
from dataclasses import dataclass

from mediator import LocalEventBus

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


async def main():
    # handlers run in background, publishing does not wait for them
    await bus.publish(MessageEvent(message="test"))
    # wait until all handlers are finished (i.e. on application shutdown)
    await bus.drain()
    # -- output --
    # first handler: test
    # second handler: test
```
Event type can have any number of handlers.
More advanced example available in [example/test_event_advanced.py](example/test_event_advanced.py) for reference.

### Event dispatching
The way event handlers are run is decided by event dispatcher:

| Dispatcher | `publish` returns | Handler error |
|---|---|---|
| `BackgroundEventDispatcher` (default) | immediately, handlers run as background tasks | passed to `on_error` callable, logged by default |
| `AwaitingEventDispatcher` | when all handlers are finished | raised from `publish` as `ExceptionGroup`, other handlers still run |

```python
from mediator import AwaitingEventDispatcher, BackgroundEventDispatcher, LocalEventBus

# useful in tests or when event has to be processed before going further
bus = LocalEventBus(dispatcher=AwaitingEventDispatcher())

# custom reaction on handler failure
bus = LocalEventBus(
    dispatcher=BackgroundEventDispatcher(
        on_error=lambda action, error: print(f"{action.subject} failed: {error!r}")
    )
)
```
Custom strategy is any object with `dispatch` and `drain` methods (see `EventDispatcher`).

## Handler for many types
Handler with union type annotation is registered for all types of union:
```python
@bus.register
async def audit_handler(event: UserCreated | UserDeleted): ...
```

## Extra parameters injection
Keyword arguments given on execution or publishing are passed to handlers
that declare them, other handlers simply do not get them:
```python
@bus.register
async def command_handler(command: PrintMessageCommand, user: str):
    print(f"{user} prints: {command.message}")


await bus.execute(PrintMessageCommand(message="test"), user="admin", trace_id="1234")
```

## Modifiers
Modifier wraps handler execution. Modifier stack can be defined for whole bus,
for registry or for single handler:
```python
from mediator import ActionCallType, ActionResult, ActionSubject, LocalRequestBus


class LogModifierFactory:
    def create(self, call: ActionCallType, *, target: ActionCallType) -> ActionCallType:
        async def wrapper(action: ActionSubject) -> ActionResult:
            print(f"before: {action.subject}")
            result = await call(action)
            print(f"after: {result.result}")
            return result

        return wrapper


bus = LocalRequestBus(modifiers=[LogModifierFactory()])
```

## Development
Project uses [uv](https://docs.astral.sh/uv/):
```shell
uv sync                 # create environment
uv run pytest           # tests
uv run ruff check .     # lints
uv run ruff format .    # code formatting
uv run mypy             # static type check
```
