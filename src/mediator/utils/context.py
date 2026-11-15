from typing import Generic, TypeVar

T = TypeVar("T")


class AsyncNullContextManager(Generic[T]):
    """
    Asyncio null context manager - zero functionality context manager.
    """

    def __init__(self, return_value: T | None = None):
        """
        Initializes asyncio null context manager.
        :param return_value: optional value returned in `when` statement
        """
        self.return_value = return_value

    async def __aenter__(self):
        return self.return_value

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
