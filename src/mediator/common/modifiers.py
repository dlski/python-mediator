from collections.abc import Sequence
from typing import Protocol

from mediator.common.types import ActionCallType


class ModifierFactory(Protocol):
    """
    Modifier factory.

    Factory that produces action callable,
    that wraps given callable into it with extra behaviour.
    """

    def create(self, call: ActionCallType, *, target: ActionCallType) -> ActionCallType:
        """
        Produces action callable that wraps given one with extra behaviour.

        Example:
        >>> class SomeModifierFactory:
        >>>     def create(
        >>>         self, call: ActionCallType, *, target: ActionCallType
        >>>     ) -> ActionCallType:
        >>>         async def wrapper(action: ActionSubject) -> ActionResult:
        >>>             # ... extra logic for arguments inspection or modification
        >>>             result = await call(action)
        >>>             # ... extra logic for result inspection or modification
        >>>             return result
        >>>
        >>>         return wrapper

        :param call: callable to be wrapped
        :param target: final callable in stack (if stack of modifiers is built);
        it is a `Handler` object when stack is built by handler registry
        :return: wrapped action callable that calls given one
        and acts with arguments or result
        """
        ...


class ModifierStack:
    """
    Utility for build modifier stacks that wraps action callable.
    """

    @classmethod
    def build(
        cls, factories: Sequence[ModifierFactory], call: ActionCallType
    ) -> ActionCallType:
        """
        Builds modifier stack action callable wrapper from factory sequence.

        Factory sequence is projected directly onto call trace.
        For example: if factories `[Af, Bf, Cf]` produce `[A, B, C]` modifiers,
        call stack will be organized as: `A -> B -> C -> call`
        :param factories: sequence of modifier factory
        to wrap given callable recursively
        :param call: action callable to be recursively wrapped by modifiers
        :return: wrapped action callable
        that contains behaviour of all modifiers in given order
        """
        target = call
        for factory in reversed(factories):
            call = factory.create(call, target=target)
        return call
