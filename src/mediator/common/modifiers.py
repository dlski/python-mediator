from typing import Sequence

from mediator.common.types import (  # noqa F401
    ActionCallType,
    ActionResult,
    ActionSubject,
)


class ModifierFactory:
    """
    Modifier factory.

    Factory that produces action callable,
    that wraps given callable into it with extra behaviour.
    """

    def create(self, call: ActionCallType, **kwargs) -> ActionCallType:
        """
        Produces action callable that wraps given one with extra behaviour.

        Example:
        >>> class SomeModifierFactory:
        >>>     def create(self, call: ActionCallType, **kwargs) -> ActionCallType:
        >>>         async def wrapper(action: ActionSubject) -> ActionResult:
        >>>             # ... extra logic for arguments inspection or modification
        >>>             result = await call(action)
        >>>             # ... extra logic for result inspection or modification
        >>>             return result
        >>>
        >>>         return wrapper

        :param call: callable to be wrapped
        :param kwargs: extra context information; currently contains:
        target - final callable in stack (if stack of modifiers is built)
        :return: wrapped action callable that calls given one
        and acts with arguments or result
        """
        raise NotImplementedError


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
