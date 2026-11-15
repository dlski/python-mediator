from collections.abc import Sequence

from mediator.common.factory import (
    CallableHandlerPolicy,
    HandlerFactoryCascade,
    PolicyType,
)
from mediator.common.modifiers import ModifierFactory
from mediator.common.registry import HandlerRegistry, MappingHandlerStore


class RequestHandlerRegistry(HandlerRegistry):
    """
    Event handler registry class.

    Registry that registers (adds) and stores request handlers.
    """

    def __init__(
        self,
        policies: Sequence[PolicyType] | None = None,
        cascade: HandlerFactoryCascade | None = None,
        modifiers: Sequence[ModifierFactory] = (),
    ) -> None:
        """
        Initializes request handler registry.
        :param policies:
        (optional) sequence of policies to be used as recipe
        to convert raw objects into handlers;
        if not provided default CallableHandlerPolicy is used;
        overwritten when cascade is provided
        :param cascade:
        (optional/advanced) custom handler factory cascade to customize
        policy into handler factory mapping
        :param modifiers: sequence of modifiers to be applied on new handler entries
        """
        super().__init__(
            store=MappingHandlerStore(),
            policies=policies or [CallableHandlerPolicy()],
            cascade=cascade,
            modifiers=modifiers,
        )
