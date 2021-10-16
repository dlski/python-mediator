from typing import Any, Iterable, Sequence

from mediator.common.handler import Handler


class HandlerFactoryError(Exception):
    """
    General handler factory error class.

    All sub error classes related to handler factory inherits form it.
    """


class IncompatibleHandlerFactoryError(TypeError, HandlerFactoryError):
    """
    Incompatible handler factory error.

    Error is raised when given handler factory input cannot be processed
    due to its incompatibility to the factory specification.
    """


class HandlerFactory:
    """
    Handler factory is an abstraction over action handler creation
    form underlying object.
    """

    def create(self, obj: Any) -> Handler:
        raise NotImplementedError


class HandlerFactoryMapper:
    """"""

    def map_all(self, policies: Iterable[Any]) -> Sequence[HandlerFactory]:
        return [self.map(policy) for policy in policies]

    def map(self, policy: Any) -> HandlerFactory:
        raise NotImplementedError
