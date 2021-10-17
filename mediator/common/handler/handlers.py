from typing import (
    Any,
    Awaitable,
    Callable,
    Collection,
    Dict,
    Hashable,
    Mapping,
    Optional,
    Tuple,
)

from mediator.common.handler.base import Handler
from mediator.common.types import ActionResult, ActionSubject


class CallableHandler(Handler):
    """
    Customisable callable handler.
    Simply invokes underlying callable
    with prepared arguments sourced from action object.
    """

    __slots__ = ("_obj", "_fn", "_key", "_arg_map", "_arg_filter", "_args")

    def __init__(
        self,
        obj: Any,
        fn: Callable[..., Awaitable[Any]],
        key: Hashable,
        subject_name: Optional[str],
        arg_map: Mapping[str, str],
        allow_args: Optional[Collection[str]],
    ):
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
        self._arg_map = self._arg_map_factory(arg_map)
        self._arg_filter = self._arg_filter_factory(allow_args)
        self._args = self._args_factory(subject_name)

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
        kwargs = self._arg_map(action.inject)
        kwargs = self._arg_filter(kwargs)
        args, kwargs = self._args(action.subject, kwargs)
        result = await self._fn(*args, **kwargs)
        return ActionResult(result)

    @classmethod
    def _arg_map_factory(cls, arg_map: Mapping[str, str]):
        """
        Argument mapping factory.
        Provides function that maps dictionary of keyword args
        to another one that fits into callable spec.
        :param arg_map: action arg name into callable arg name mapping
        :return: function that performs keyword args dict mapping
        """
        if arg_map:

            def _arg_map(kwargs: Dict[str, Any]):
                return {
                    arg_map.get(name, name): value for name, value in kwargs.items()
                }

        else:

            def _arg_map(kwargs: Dict[str, Any]):
                return kwargs

        return _arg_map

    @classmethod
    def _arg_filter_factory(cls, allow_args: Optional[Collection[str]]):
        """
        Argument filter factory.
        Provides function that filters dictionary of underlying callable keyword args.
        :param allow_args: collection of action only necessary argument names,
        used to make filter removing excessive arguments
        that may not fit into callable signature
        :return: function that filters dictionary of underlying callable keyword args
        """
        if allow_args is None:

            def _arg_filter(kwargs: Dict[str, Any]):
                return kwargs

        else:
            args = set(allow_args)

            def _arg_filter(kwargs: Dict[str, Any]):
                return {name: value for name, value in kwargs.items() if name in args}

        return _arg_filter

    @classmethod
    def _args_factory(cls, subject_name: Optional[str]):
        """
        Argument former factory.
        Provides function that forms underlying callable *args and **kwargs
        regarding to subject (main argument name) name .
        :param subject_name: main argument name;
        when is not None, action main argument (subject) is provided as keyword arg,
        else action main argument (subject) is placed as positional one
        :return: function that forms underlying callable *args and **kwargs
        """
        if subject_name:

            def _args(
                subject: Any, kwargs: Dict[str, Any]
            ) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
                kwargs[subject_name] = subject  # type: ignore
                return (), kwargs

        else:

            def _args(
                subject: Any, kwargs: Dict[str, Any]
            ) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
                return (subject,), kwargs

        return _args
