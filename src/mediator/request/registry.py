from typing import Optional, Sequence

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
        policies: Optional[Sequence[PolicyType]] = None,
        cascade: Optional[HandlerFactoryCascade] = None,
        modifiers: Sequence[ModifierFactory] = (),
    ):
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
        HandlerRegistry.__init__(
            self,
            store=MappingHandlerStore(),
            policies=policies or [CallableHandlerPolicy()],
            cascade=cascade,
            modifiers=modifiers,
        )
