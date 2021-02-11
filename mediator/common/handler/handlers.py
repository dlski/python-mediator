from typing import Any, Awaitable, Callable, Dict, Hashable, Optional, Tuple

from mediator.common.handler.base import Handler
from mediator.common.types import ActionResult, ActionSubject


class DirectHandler(Handler):
    def __init__(self, handler: Any, fn: Callable[..., Awaitable[Any]], key: Hashable):
        self.handler = handler
        self._fn = fn
        self._key = key

    @property
    def key(self) -> Hashable:
        return self._key

    async def __call__(self, action: ActionSubject) -> ActionResult:
        result = await self._fn(action.subject, **action.inject)
        return ActionResult(result)


class MappedDirectHandler(DirectHandler):
    def __init__(
        self,
        handler: Any,
        fn: Callable[..., Awaitable[Any]],
        key: Hashable,
        subject_name: Optional[str],
        arg_map: Dict[str, str],
    ):
        super().__init__(handler, fn, key)
        self._arg_map = self._arg_map_factory(arg_map)
        self._args = self._args_factory(subject_name)

    async def __call__(self, action: ActionSubject) -> ActionResult:
        kwargs = self._arg_map(action.inject)
        args, kwargs = self._args(action.subject, kwargs)
        result = await self._fn(*args, **kwargs)
        return ActionResult(result)

    @classmethod
    def _arg_map_factory(cls, arg_map: Dict[str, str]):
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
    def _args_factory(cls, subject_key: Optional[str]):
        if subject_key:

            def _args(
                subject: Any, kwargs: Dict[str, Any]
            ) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
                kwargs[subject_key] = subject
                return (), kwargs

        else:

            def _args(
                subject: Any, kwargs: Dict[str, Any]
            ) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
                return (subject,), kwargs

        return _args
