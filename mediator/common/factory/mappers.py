from typing import Any, Callable, Dict, Mapping, Optional, Type

from mediator.common.factory.base import HandlerFactory, HandlerFactoryMapper
from mediator.common.factory.factories import (
    CallableHandlerFactory,
    MethodHandlerFactory,
)
from mediator.common.factory.policies import CallableHandlerPolicy, MethodHandlerPolicy


class TypeHandlerFactoryMapper(HandlerFactoryMapper):
    """
    Type handler factory mapper.

    Mapper that maps given policy into handler factory object
    using policy type to handler factory provider mapping.
    """

    def __init__(self, mapping: Mapping[Type[Any], Callable[[Any], HandlerFactory]]):
        """
        Initializes type handler factory mapper.
        :param mapping: policy type to handler factory provider mapping
        """
        self._mapping = mapping

    def map(self, policy: Any) -> HandlerFactory:
        """
        Provides handler factory object according to given policy (specification).

        :param policy: policy to map into handler factory
        :raises TypeError: when given type policy is not supported
        :return: handler factory object
        """
        policy_type = type(policy)
        handler_factory = self._mapping.get(policy_type)
        if handler_factory is None:
            raise TypeError(f"Not supported policy type {policy_type}")
        return handler_factory(policy)


class DefaultHandlerFactoryMapper(TypeHandlerFactoryMapper):
    """
    Library default handler factory mapper.

    Maps `CallableHandlerPolicy` objects and `MethodHandlerPolicy` objects
    into handler factories.
    """

    def __init__(
        self,
        extra_mapping: Optional[
            Mapping[Type[Any], Callable[[Any], HandlerFactory]]
        ] = None,
    ):
        """
        Initializes library default handler factory mapper.
        :param extra_mapping:
        extra policy mapping (policy type -> handler factory provider);
        may be used to extend or override default handler factory mapping
        """
        if extra_mapping is None:
            extra_mapping = {}
        super().__init__(
            {
                **self.default_mapping(),
                **extra_mapping,
            }
        )

    @classmethod
    def default_mapping(cls) -> Dict[Type[Any], Type[HandlerFactory]]:
        """
        Provides library default policy type to handler factory provider mapping.
        :return: default policy type to handler factory provider mapping
        """
        return {
            CallableHandlerPolicy: CallableHandlerFactory,
            MethodHandlerPolicy: MethodHandlerFactory,
        }
