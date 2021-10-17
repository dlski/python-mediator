from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Hashable


@dataclass
class ActionSubject:
    """
    Unified action subject.
    Holds primary and extra injection arguments for action handler.
    """

    subject: Any
    inject: Dict[str, Any]

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
