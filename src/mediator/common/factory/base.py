from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from typing import Any, Protocol

from mediator.common.handler import Handler


class HandlerFactoryError(Exception):
    """
    Handler factory error base class.

    All sub error classes related to handler factory inherits form it.
    """


class IncompatibleHandlerFactoryError(TypeError, HandlerFactoryError):
    """
    Incompatible handler factory error.

    Error is raised when given handler factory input cannot be processed
    due to its incompatibility to the factory specification.
    """


class HandlerFactory(Protocol):
    """
    Handler factory is an abstraction over action handler creation
    form underlying object.
    """

    def create(self, obj: Any) -> Sequence[Handler]:
        """
        Creates handlers for given object.

        Usually single handler is created, but object that accepts
        many action subject types (like `A | B`) gets one handler for each type.
        :param obj: object to create handlers for
        :raises IncompatibleHandlerFactoryError: when object is incompatible
        with factory specification
        :raises HandlerFactoryError: when there is failure during object inspection
        :return: handlers for given object
        """
        ...


class HandlerFactoryMapper(ABC):
    """
    Handler factory mapper abstraction.
    Maps policy (specification) into handler factory object.
    """

    def map_all(self, policies: Iterable[Any]) -> Sequence[HandlerFactory]:
        """
        Maps all policies (specifications) into handler factory object
        :param policies: iterable providing sequence of policies (specifications)
        :return: sequence of handler factory objects
        """
        return [self.map(policy) for policy in policies]

    @abstractmethod
    def map(self, policy: Any) -> HandlerFactory:
        """
        Maps given policy (specification) into handler factory
        :param policy: given policy (specification)
        :return: handler factory object
        """
