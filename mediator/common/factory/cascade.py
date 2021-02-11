from typing import Any, Iterable, Optional, Sequence, Tuple

from mediator.common.factory.base import (
    HandlerFactoryError,
    IncompatibleHandlerFactoryError,
)
from mediator.common.factory.mappers import (
    DefaultHandlerFactoryMapper,
    HandlerFactory,
    HandlerFactoryMapper,
)
from mediator.common.factory.policies import PolicyType
from mediator.common.handler import Handler


class HandlerFactoryCascadeError(Exception):
    pass


class ConfigHandlerFactoryCascadeError(ValueError, HandlerFactoryCascadeError):
    pass


class InspectionHandlerFactoryCascadeError(HandlerFactoryCascadeError):
    def __init__(self, *args, factory: HandlerFactory):
        super().__init__(*args)
        self.factory = factory


class IncompatibleHandlerFactoryCascadeError(HandlerFactoryCascadeError):
    def __init__(
        self,
        *args,
        factory_errors: Sequence[
            Tuple[HandlerFactory, IncompatibleHandlerFactoryError]
        ],
    ):
        super().__init__(*args)
        self.factory_errors = factory_errors


class HandlerFactoryCascade:
    def __init__(
        self,
        policies: Iterable[PolicyType],
        mapper: Optional[HandlerFactoryMapper] = None,
    ):
        policies = [*policies]
        if not policies:
            raise ConfigHandlerFactoryCascadeError("No policies provided")
        if mapper is None:
            mapper = DefaultHandlerFactoryMapper()
        self._mapper = mapper
        self._factories = mapper.map_all(policies)

    def __call__(self, obj: Any) -> Handler:
        factory_errors = []
        for factory in self._factories:
            try:
                return factory.create(obj)
            except IncompatibleHandlerFactoryError as e:
                factory_errors.append((factory, e))
                continue
            except HandlerFactoryError as error:
                raise InspectionHandlerFactoryCascadeError(
                    f"Handler factory {factory!r} error for object {obj!r}: {error}",
                    factory=factory,
                ) from error
        raise IncompatibleHandlerFactoryCascadeError(
            f"Object {obj!r} is not compatible",
            factory_errors=factory_errors,
        )

    def replace(self, policies: Iterable[PolicyType]):
        return HandlerFactoryCascade(policies=policies, mapper=self._mapper)
