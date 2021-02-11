from typing import Optional, Sequence

from mediator.common.factory import HandlerFactoryCascade, PolicyType
from mediator.common.operators import OperatorDef
from mediator.common.registry import CollectionHandlerStore, HandlerRegistry


class EventHandlerRegistry(HandlerRegistry):
    def __init__(
        self,
        policies: Optional[Sequence[PolicyType]] = None,
        cascade: Optional[HandlerFactoryCascade] = None,
        operators: Sequence[OperatorDef] = (),
    ):
        HandlerRegistry.__init__(
            self,
            store=CollectionHandlerStore(),
            policies=policies,
            cascade=cascade,
            operators=operators,
        )
