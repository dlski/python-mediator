from collections.abc import Awaitable, Callable, Hashable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ActionSubject:
    """
    Unified action subject.
    Holds primary and extra injection arguments for action handler.

    Object is immutable; to pass changed subject or arguments down the call stack
    create new one, i.e. using `dataclasses.replace`.
    """

    subject: Any
    inject: dict[str, Any]

    @property
    def key(self) -> Hashable:
        """
        Action subject key. Used to find corresponding action handler.
        :return: action subject key
        """
        return type(self.subject)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class ActionResult:
    """
    Library unified action result object.
    """

    result: Any


ActionCallType = Callable[[ActionSubject], Awaitable[ActionResult]]
