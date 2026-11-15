from typing import Any

from mediator.common.factory.base import HandlerFactory
from mediator.common.factory.policies import CallableHandlerPolicy, MethodHandlerPolicy
from mediator.common.factory.utils import (
    create_callable_handler,
    inspect_attribute,
    inspect_callable,
)
from mediator.common.handler import Handler


class CallableHandlerFactory(HandlerFactory):
    """
    Callable handler factory.

    Factory that produces callable handler directly from callable object.
    """

    def __init__(self, policy: CallableHandlerPolicy) -> None:
        """
        Initializes callable handler factory.
        :param policy: policy used as a configuration or specification
        for producing handler object
        """
        self._policy = policy

    def create(self, obj: Any) -> Handler:
        """
        Creates handler directly form callable object.
        :param obj: callable object
        :raises IncompatibleHandlerFactoryError: when callable object is incompatible
        with factory specification
        :raises HandlerFactoryError: when there is failure during object inspection
        :return: handler invoking given callable object
        """
        details = inspect_callable(obj)
        return create_callable_handler(details, obj=obj, policy=self._policy)


class MethodHandlerFactory(HandlerFactory):
    """
    Method handler factory.

    Factory that produces callable handler from given object attribute
    - in most cases method.
    """

    def __init__(self, policy: MethodHandlerPolicy) -> None:
        """
        Initializes method handler factory.
        :param policy: policy used as a configuration or specification
        for producing handler object
        """
        self._policy = policy

    def create(self, obj: Any) -> Handler:
        """
        Creates handler from given object attribute according to specification.
        :param obj: callable object
        :raises IncompatibleHandlerFactoryError: when callable object is incompatible
        with factory specification
        :raises HandlerFactoryError: when there is failure during object inspection
        :return: handler invoking given object callable attribute
        """
        policy = self._policy
        details = inspect_attribute(obj, policy.name, policy.subtype_of)
        return create_callable_handler(details, obj=obj, policy=policy.policy)
