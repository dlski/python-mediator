from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class AsyncNullContextManager(Generic[T]):
    def __init__(self, return_value: Optional[T] = None):
        self.return_value = return_value

    async def __aenter__(self):
        return self.return_value

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
