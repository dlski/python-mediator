from collections.abc import Hashable
from typing import Any, Protocol, runtime_checkable

from mediator.common.types import ActionResult, ActionSubject


class HandlerInfo(Protocol):
    """
    An abstraction that defines handler specification interface.
    """

    __slots__ = ()

    @property
    def key(self) -> Hashable:
        """
        Provides unique key that will be used to match given handler with action.
        :return: hashable key
        """
        ...

    @property
    def obj(self) -> Any:
        """
        Provides handler related object - source of handler behaviour
        :return: handler related object - source of handler behaviour
        """
        ...


@runtime_checkable
class Handler(HandlerInfo, Protocol):
    """
    An abstraction that unifies the handler specification and invocation interface.
    Is an adapter to the underlying object complexity.
    """

    __slots__ = ()

    async def __call__(self, action: ActionSubject) -> ActionResult:
        """
        Performs handler action with given argument values.
        :param action: action subject including argument values
        :return: action result object including return value
        """
        ...
