from dataclasses import dataclass
from typing import Hashable, Iterable, Iterator, Sequence

from mediator.common.handler.base import Handler
from mediator.common.modifiers import ModifierFactory, ModifierStack
from mediator.common.types import ActionCallType


@dataclass
class HandlerEntry:
    """
    Handler entry - combines handler with call modifiers.
    """

    handler: Handler
    modifiers: Sequence[ModifierFactory] = ()

    @property
    def key(self) -> Hashable:
        """
        Provides unique key that will be used to match given handler with action.
        :return: hashable key
        """
        return self.handler.key

    def handler_pipeline(self) -> ActionCallType:
        """
        Builds pipeline for given handler including all call modifiers.
        :return: pipeline callable compatible with handler interface
        """
        return self.pipeline(self.handler)

    def pipeline(self, call: ActionCallType) -> ActionCallType:
        """
        Builds pipeline for given action callable
        including all call modifiers.
        :param call: action callable to be wrapped by modifiers
        :return: pipeline callable compatible with handler interface
        """
        return ModifierStack.build(self.modifiers, call)

    def stack(self, modifiers: Sequence[ModifierFactory]) -> "HandlerEntry":
        """
        Produces new handler entry with added new modifier factories on top.
        :param modifiers: modifiers to add on top/in front of given entry ones
        :return: new handler entry with extender modifier stack
        """
        return HandlerEntry(
            handler=self.handler,
            modifiers=tuple([*modifiers, *self.modifiers]),
        )


class HandlerStoreError(Exception):
    """
    Base handler store error.
    """


class InspectionHandlerStoreError(HandlerStoreError):
    """
    Inspection handler store error.

    Raised when given handler store implementation
    performs object inspection (i.e. using handler factory).
    """


class CollisionHandlerStoreError(KeyError, HandlerStoreError):
    """
    Collision handler store error.

    Raised when given handler store implementation
    has handler entry indexation (i.e. using handler key)
    and internal constraints rejects trial of storing given key duplicate.
    """


class LookupHandlerStoreError(LookupError, HandlerStoreError):
    """
    Lookup handler store error.

    Raised when given handler store implementation
    has lookup mechanisms (i.e. using handler key)
    and fails to find given entry by key.
    """


class HandlerStore:
    """
    Handler store abstraction.

    Handler stores are used for storing handler entries.
    """

    def add(self, entry: HandlerEntry):
        """
        Adds given handler entry into store.
        :param entry: handler entry to add into store
        """
        raise NotImplementedError

    def include(self, entries: Iterable[HandlerEntry]):
        """
        Adds all handler entries from given iterable into store.
        :param entries: handler entries iterator
        """
        raise NotImplementedError

    def __iter__(self) -> Iterator[HandlerEntry]:
        """
        Returns iterator providing all underlying store handler entries.
        :return: iterator providing all underlying store handler entries.
        """
        raise NotImplementedError
