from dataclasses import dataclass

import pytest

from mediator.common.factory import CallableHandlerPolicy, MethodHandlerPolicy
from mediator.request import LocalRequestBus, RequestHandlerRegistry

# Create local request registry with given policies.
# Single policy tells the handler inspector where to find callable
# which handles particular action.
# - add policy that suggest to get object attribute named "execute"
#   and try to analyze as request handler
# - add policy that suggest given object is request handler callable
registry = RequestHandlerRegistry(
    policies=[MethodHandlerPolicy(name="execute"), CallableHandlerPolicy()],
)


@dataclass
class PrintCommand:
    message: str


class PrintCommandHandler:
    # noinspection PyMethodMayBeStatic
    async def execute(self, command: PrintCommand):
        print(f"print: {command.message}")
        return command.message


# ... MethodHandlerPolicy(...) gives ability to inspect handler object

handler = PrintCommandHandler()
registry.register(handler)

# ... CallableHandlerPolicy(...) gives ability to inspect plain function


@dataclass
class DataQuery:
    entry_id: int


@registry.register
async def data_query_handler(query: DataQuery):
    print(f"entry loaded: {query.entry_id}")
    return {"id": query.entry_id, "data": "test"}


@pytest.mark.asyncio
async def test_request_advanced():
    # create local request bus and include handlers from registry
    bus = LocalRequestBus()
    # registry usage is optional - used for example purposes,
    # LocalRequestBus implements same registry interface
    bus.include(registry)

    # execute command
    printed_message = await bus.execute(PrintCommand(message="test"))
    assert printed_message == "test"

    # execute query
    data = await bus.execute(DataQuery(entry_id=1))
    assert data == {"id": 1, "data": "test"}
