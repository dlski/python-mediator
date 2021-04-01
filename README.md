# python-mediator

[![CI](https://github.com/dlski/python-mediator/actions/workflows/ci.yml/badge.svg?branch=master&event=push)](https://github.com/dlski/python-mediator/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/dlski/python-mediator/branch/master/graph/badge.svg?token=AU4T4Z81F6)](https://codecov.io/gh/dlski/python-mediator)
[![pypi](https://img.shields.io/pypi/v/python-mediator.svg)](https://pypi.python.org/pypi/python-mediator)
[![downloads](https://img.shields.io/pypi/dm/python-mediator.svg)](https://pypistats.org/packages/python-mediator)
[![versions](https://img.shields.io/pypi/pyversions/python-mediator.svg)](https://github.com/dlski/python-mediator)
[![license](https://img.shields.io/github/license/dlski/python-mediator.svg)](https://github.com/dlski/python-mediator/blob/master/LICENSE)

Elastic and extensible asyncio CQRS + ES python microframework.
Compatible with recent python versions: 3.7, 3.8, 3.9, pypy3.

Corresponds to clean architecture patterns, ideal for
command/query segregation scenarios and event-driven design approaches.
No external dependencies - uses only standard libraries.

Key features:
- automatic function or method handler inspection -
  proper action (command/query/event) to handler matching is fully automatic
  and based on python type hints (annotations) by default
- configurable middleware (operator) stack -
  handler call flow can be extended easily
  with i.e. data mapping, special exception handling or extra logging
- configurable extra parameters injection
- elastic and extensible -
  custom behaviours and custom transport backends can be adapted with small effort

## Help
Coming soon...

## A command/query handling example
```python
from dataclasses import dataclass

from mediator.request import LocalRequestBus

bus = LocalRequestBus()


@dataclass
class PrintMessageCommand:
    message: str


@bus.register
async def command_handler(event: PrintMessageCommand):
    print(f"print message: {event.message}")
    return event.message


@dataclass
class DataQuery:
    id: int


@bus.register
async def query_handler(query: DataQuery):
    print(f"data query: {query.id}")
    return {"id": query.id, "data": "test"}


async def main():
    printed_message = await bus.execute(PrintMessageCommand(message="test"))
    assert printed_message == "test"

    data = await bus.execute(DataQuery(id=1))
    assert data == {"id": 1, "data": "test"}

    # -- output --
    # print message: test
    # data query: 1

```
More advanced example available in [tests/example/test_request_advanced.py](tests/example/test_request_advanced.py) for reference.

## An event handling example
```python
from dataclasses import dataclass

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


async def main():
    await bus.publish(MessageEvent(message="test"))
    # -- output --
    # first handler: test
    # second handler: test
```
More advanced example available in [tests/example/test_event_advanced.py](tests/example/test_event_advanced.py) for reference.
