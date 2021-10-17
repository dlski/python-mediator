from typing import Any, Iterable, Sequence

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


class HandlerFactory:
    """
    Handler factory is an abstraction over action handler creation
    form underlying object.
    """

    def create(self, obj: Any) -> Handler:
        raise NotImplementedError


class HandlerFactoryMapper:
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

    def map(self, policy: Any) -> HandlerFactory:
        """
        Maps given policy (specification) into handler factory
        :param policy: given policy (specification)
        :return: handler factory object
        """
        raise NotImplementedError
