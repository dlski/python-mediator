from typing import Any, Iterable, Sequence

from mediator.common.handler import Handler


class HandlerFactoryError(Exception):
    pass


class IncompatibleHandlerFactoryError(TypeError, HandlerFactoryError):
    pass


class HandlerFactory:
    def create(self, obj: Any) -> Handler:
        raise NotImplementedError


class HandlerFactoryMapper:
    def map_all(self, policies: Iterable[Any]) -> Sequence[HandlerFactory]:
        return [self.map(policy) for policy in policies]

    def map(self, policy: Any) -> HandlerFactory:
        raise NotImplementedError
