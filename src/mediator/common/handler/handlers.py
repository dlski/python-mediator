from collections.abc import Awaitable, Callable, Collection, Hashable, Mapping
from typing import Any

from mediator.common.handler.base import Handler
from mediator.common.types import ActionResult, ActionSubject


class CallableHandler(Handler):
    """
    Customisable callable handler.
    Simply invokes underlying callable
    with prepared arguments sourced from action object.
    """

    __slots__ = ("_allow_args", "_arg_map", "_fn", "_key", "_obj", "_subject_name")

    def __init__(
        self,
        obj: Any,
        fn: Callable[..., Awaitable[Any]],
        key: Hashable,
        subject_name: str | None,
        arg_map: Mapping[str, str],
        allow_args: Collection[str] | None,
    ) -> None:
        """
        Creates callable handler object.
        :param obj: object used as information of handler behaviour source
        :param fn: callable to invoke by handler
        :param key: handler hashable key
        :param subject_name: main argument name;
        when is not None, action main argument (subject) is provided as keyword arg,
        else action main argument (subject) is placed as positional one
        :param arg_map: argument map;
        used to make translation of action extra argument names
        to fit callable signature
        :param allow_args: collection of action only necessary argument names,
        used to make filter removing excessive arguments
        that may not fit into callable signature
        """
        self._obj = obj
        self._fn = fn
        self._key = key
        self._subject_name = subject_name or None
        self._arg_map = dict(arg_map)
        self._allow_args = None if allow_args is None else frozenset(allow_args)

    @property
    def key(self) -> Hashable:
        """
        Provides unique key that will be used to match given handler with action.
        :return: hashable key
        """
        return self._key

    @property
    def obj(self) -> Any:
        """
        Provides handler underlying object
        :return: handler underlying object
        """
        return self._obj

    async def __call__(self, action: ActionSubject) -> ActionResult:
        """
        Performs arguments mapping, filtering and invokes underlying callable.
        :param action: action containing call values
        :return: callable returned value wrapped into `ActionResult` object
        """
        kwargs = self._kwargs(action.inject)
        if self._subject_name is None:
            result = await self._fn(action.subject, **kwargs)
        else:
            kwargs[self._subject_name] = action.subject
            result = await self._fn(**kwargs)
        return ActionResult(result)

    def _kwargs(self, inject: Mapping[str, Any]) -> dict[str, Any]:
        """
        Forms underlying callable keyword arguments from action extra arguments:
        translates names using argument map and drops not allowed ones.
        :param inject: action extra arguments
        :return: new dictionary of callable keyword arguments;
        action extra arguments are never modified
        """
        arg_map = self._arg_map
        if arg_map:
            kwargs = {arg_map.get(name, name): value for name, value in inject.items()}
        else:
            kwargs = dict(inject)
        allow_args = self._allow_args
        if allow_args is not None:
            kwargs = {
                name: value for name, value in kwargs.items() if name in allow_args
            }
        return kwargs
