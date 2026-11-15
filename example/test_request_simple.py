from dataclasses import dataclass

import pytest

from mediator.request import LocalRequestBus, Request

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


@pytest.mark.asyncio
async def test_request_simple():
    printed_message = await bus.execute(PrintMessageCommand(message="test"))
    assert printed_message == "test"

    data = await bus.execute(DataQuery(id=1))
    assert data == {"id": 1, "data": "test"}

    # -- output --
    # print message: test
    # data query: 1
