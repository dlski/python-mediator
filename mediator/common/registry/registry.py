import functools
from typing import Any, Iterable, Iterator, Optional, Sequence

from mediator.common.factory.cascade import HandlerFactoryCascade
from mediator.common.factory.policies import PolicyType
from mediator.common.modifiers import ModifierFactory
from mediator.common.registry.base import HandlerEntry, HandlerStore
from mediator.common.registry.stores import ModifierHandlerStore


class HandlerRegistry(HandlerStore):
    """
    Handler registry class.

    Facade that joins modified handler store functionality
    with ability to add handlers directly created from raw objects.
    """

    def __init__(
        self,
        store: HandlerStore,
        policies: Optional[Sequence[PolicyType]] = None,
        cascade: Optional[HandlerFactoryCascade] = None,
        modifiers: Sequence[ModifierFactory] = (),
    ):
        """
        Initializes handler registry.
        :param store: underlying handler store used for handler entry storage
        :param policies:
        (optional) sequence of policies to be used as recipe
        to convert raw objects into handlers;
        if not provided cascade argument should be set;
        is overwritten when cascade is provided
        :param cascade:
        (optional) custom handler factory cascade to customize
        policy into handler factory mapping;
        if not provided policies argument should be set
        :param modifiers: sequence of modifiers to be applied on new handler entries
        """
        if cascade is not None:
            self._cascade = cascade
        elif policies is not None:
            self._cascade = HandlerFactoryCascade(policies)
        else:
            raise TypeError("policies or cascade argument should be provided")
        self._store = ModifierHandlerStore.wrap(nested=store, modifiers=modifiers)

    def register(
        self,
        obj: Optional[Any] = None,
        *,
        policies: Optional[Sequence[PolicyType]] = None,
        modifiers: Sequence[ModifierFactory] = (),
    ):
        """
        Registers given raw object as an action handler
        or provides decorator that registers given raw object as an action handler.
        :param obj: (optional) raw handler object (like function)
        :param policies:
        custom one time polices to be used in object inspection process
        :param modifiers:
        custom one time modifiers to be applied on given object handler
        :return: returns given raw object or decorator, when no object is provided
        """
        cascade = self._policies_cascade(policies)
        if obj is None:
            register = functools.partial(
                self._process_obj, cascade=cascade, modifiers=modifiers
            )

            def wrap(fn: Any):
                register(fn)
                return fn

            return wrap

        else:
            self._process_obj(obj, cascade=cascade, modifiers=modifiers)
            return obj

    def _policies_cascade(
        self, policies: Optional[Sequence[PolicyType]]
    ) -> HandlerFactoryCascade:
        """
        Provides handler factory cascade customized with given policies.
        If no policies are provided uses unchanged underlying cascade.
        :param policies: policies to customize handler factory cascade
        :return: cascade with applied new policies (if any)
        """
        if policies is None:
            return self._cascade
        else:
            return self._cascade.replace(policies)

    def _process_obj(
        self,
        obj: Any,
        *,
        cascade: HandlerFactoryCascade,
        modifiers: Sequence[ModifierFactory],
    ):
        """
        Creates handler entry for given raw action handler object.
        :param obj: raw action handler object
        :param cascade: cascade to use for handler factory
        :param modifiers: modifiers to be directly applied on given handler entry
        """
        handler = cascade(obj)
        self.add(HandlerEntry(handler=handler, modifiers=modifiers))

    def add(self, entry: HandlerEntry):
        """
        Adds given handler entry into store.
        :param entry: handler entry to add into store
        """
        self._store.add(entry)

    def include(self, entries: Iterable[HandlerEntry]):
        """
        Adds all handler entries from given iterable into store.
        :param entries: handler entries iterator
        """
        self._store.include(entries)

    def __iter__(self) -> Iterator[HandlerEntry]:
        """
        Returns iterator providing all underlying store handler entries.
        :return: iterator providing all underlying store handler entries.
        """
        return iter(self._store)
