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
    """
    Handler factory cascade base error.
    """


class ConfigHandlerFactoryCascadeError(ValueError, HandlerFactoryCascadeError):
    """
    Handler factory cascade configuration error.

    Raised when handler factory cascade is not properly configured.
    """


class InspectionHandlerFactoryCascadeError(HandlerFactoryCascadeError):
    """
    Handler factory cascade inspection error.

    Raised when one of handler factory in cascade
    raises inspection machinery failure (non usual situation) error.
    """

    def __init__(self, *args, factory: HandlerFactory):
        """
        Initializes inspection handler factory cascade error.
        :param args: python exception args
        :param factory: handler factory that raised inspection error
        """
        super().__init__(*args)
        self.factory = factory


class IncompatibleHandlerFactoryCascadeError(HandlerFactoryCascadeError):
    """
    Incompatible handler factory cascade error.

    Raised when handler factory cascade cannot convert given object into handler,
    which means `given object is incompatible and cannot be mapped`.
    """

    def __init__(
        self,
        *args,
        factory_errors: Sequence[
            Tuple[HandlerFactory, IncompatibleHandlerFactoryError]
        ],
    ):
        """
        Initializes incompatible handler factory cascade error.
        :param args: python exception args
        :param factory_errors: sequence of
        (<handler factory object>, <given handler factory error>) pairs
        """
        super().__init__(*args)
        self.factory_errors = factory_errors


class HandlerFactoryCascade:
    """
    Handler factory cascade.

    This cascade is responsible for trying to map given object into handler
    using handler factory sequence.
    """

    def __init__(
        self,
        policies: Iterable[PolicyType],
        mapper: Optional[HandlerFactoryMapper] = None,
    ):
        """
        Initializes handler factory cascade.
        :param policies: iterable providing sequence of policies
        to map into handler factories
        :param mapper: (optional)handler factory mapper
        that maps policies into corresponding handler factories;
        when not provided `DefaultHandlerFactoryMapper` is used
        :raises ConfigHandlerFactoryCascadeError: when no polices are provided
        """
        policies = [*policies]
        if not policies:
            raise ConfigHandlerFactoryCascadeError("No policies provided")
        if mapper is None:
            mapper = DefaultHandlerFactoryMapper()
        self._mapper = mapper
        self._factories = mapper.map_all(policies)

    def __call__(self, obj: Any) -> Handler:
        """
        Tries to create handler object for given python object
        (compatible with cascade policy sequence).
        :param obj: any compatible python object
        :raises InspectionHandlerFactoryCascadeError:
        when failure occurs during object inspection
        :raises IncompatibleHandlerFactoryCascadeError:
        when object cannot be mapped by any handler factory -
        is incompatible cascade configuration
        :return: handler object for given python object
        """
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

    def replace(self, policies: Iterable[PolicyType]) -> "HandlerFactoryCascade":
        """
        Creates new handler factory cascade that has replaced policy sequence,
        but uses the same policy to handler factory mapper.
        :param policies: iterable providing new sequence of policies (specifications)
        :return: new handler policy cascade initialized using new set of policies
        and same handler factory mapper
        """
        return HandlerFactoryCascade(policies=policies, mapper=self._mapper)
