from typing import Any


class RequestExecutor:
    async def execute(self, obj: Any, **kwargs) -> Any:
        raise NotImplementedError
