from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Hashable


@dataclass
class ActionSubject:
    subject: Any
    inject: Dict[str, Any]

    @property
    def key(self) -> Hashable:
        return type(self.subject)


@dataclass
class ActionResult:
    result: Any


ActionCallType = Callable[[ActionSubject], Awaitable[ActionResult]]
