from typing import Any


class RequestExecutor:
    """
    An abstraction that orders request executor interface.
    """

    async def execute(self, obj: Any, **kwargs) -> Any:
        """"""
        raise NotImplementedError
