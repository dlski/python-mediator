from typing import Any, Callable, Hashable, Type

import pytest

from mediator.common.handler import Handler
from mediator.common.types import ActionResult, ActionSubject


class MockupHandler(Handler):
    def __init__(self, type_: Type):
        self.type_ = type_

    @property
    def key(self) -> Hashable:
        return self.type_  # type: ignore

    @property
    def obj(self) -> Any:
        return self.type_

    async def __call__(self, action: ActionSubject) -> ActionResult:
        return ActionResult(result=(action.subject, action.inject))


@pytest.fixture
def mockup_action_factory() -> Callable[[], ActionSubject]:
    def create_action():
        return ActionSubject("test", inject={})

    return create_action
