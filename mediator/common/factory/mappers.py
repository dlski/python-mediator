from typing import Any, Callable, Mapping, Optional, Type

from mediator.common.factory.base import HandlerFactory, HandlerFactoryMapper
from mediator.common.factory.factories import (
    CallableHandlerFactory,
    MethodHandlerFactory,
)
from mediator.common.factory.policies import CallableHandlerPolicy, MethodHandlerPolicy


class TypeHandlerFactoryMapper(HandlerFactoryMapper):
    def __init__(self, mapping: Mapping[Type, Callable[[Any], HandlerFactory]]):
        self._mapping = mapping

    def map(self, policy: Any) -> HandlerFactory:
        policy_type = type(policy)
        handler_factory = self._mapping.get(policy_type)
        if handler_factory is None:
            raise TypeError(f"Not supported policy type {policy_type}")
        return handler_factory(policy)


class DefaultHandlerFactoryMapper(TypeHandlerFactoryMapper):
    def __init__(
        self,
        extra_mapping: Optional[Mapping[Type, Callable[[Any], HandlerFactory]]] = None,
    ):
        if extra_mapping is None:
            extra_mapping = {}
        super().__init__(
            {
                **self.default_mapping(),
                **extra_mapping,
            }
        )

    @classmethod
    def default_mapping(cls):
        return {
            CallableHandlerPolicy: CallableHandlerFactory,
            MethodHandlerPolicy: MethodHandlerFactory,
        }
