from typing import Any, Hashable

from mediator.common.types import ActionResult, ActionSubject


class HandlerInfo:
    """
    An abstraction that defines handler specification interface.
    """

    @property
    def key(self) -> Hashable:
        """
        Provides unique key that will be used to match given handler with action.
        :return: hashable key
        """
        raise NotImplementedError

    @property
    def obj(self) -> Any:
        """
        Provides handler related object - source of handler behaviour
        :return: handler related object - source of handler behaviour
        """
        raise NotImplementedError


class Handler(HandlerInfo):
    """
    An abstraction that unifies the handler specification and invocation interface.
    Is an adapter to the underlying object complexity.
    """

    @property
    def key(self) -> Hashable:
        """
        Provides unique key that will be used to match given handler with action.
        :return: hashable key
        """
        raise NotImplementedError

    @property
    def obj(self) -> Any:
        """
        Provides handler related object - source of handler behaviour
        :return: handler related object - source of handler behaviour
        """
        raise NotImplementedError

    async def __call__(self, action: ActionSubject) -> ActionResult:
        """
        Performs handler action with given argument values.
        :param action: action subject including argument values
        :return: action result object including return value
        """
        raise NotImplementedError
