from collections.abc import Awaitable, Callable, Hashable
from dataclasses import dataclass
from typing import Any


@dataclass
class ActionSubject:
    """
    Unified action subject.
    Holds primary and extra injection arguments for action handler.
    """

    subject: Any
    inject: dict[str, Any]

    @property
    def key(self) -> Hashable:
        """
        Action subject key. Used to find corresponding action handler.
        :return: action subject key
        """
        return type(self.subject)  # type: ignore


@dataclass
class ActionResult:
    """
    Library unified action result object.
    """

    result: Any


ActionCallType = Callable[[ActionSubject], Awaitable[ActionResult]]
