from typing import Any, Generic, Protocol, TypeVar, overload

R = TypeVar("R")
R_co = TypeVar("R_co", covariant=True)


class Request(Generic[R_co]):
    """
    Optional base class for request objects, that declares request result type.

    Request executor returns precise result type for objects of such classes:
    >>> @dataclass(frozen=True)
    >>> class GetUserName(Request[str]):
    >>>     user_id: int
    >>>
    >>> name = await bus.execute(GetUserName(user_id=1))  # type checker knows: str

    Usage is not required: any object can be a request,
    in that case result type is not known to type checker.
    """

    __slots__ = ()


class RequestExecutor(Protocol):
    """
    Request executor interface.
    """

    @overload
    async def execute(self, obj: Request[R], **kwargs: Any) -> R: ...

    @overload
    async def execute(self, obj: Any, **kwargs: Any) -> Any: ...

    async def execute(self, obj: Any, **kwargs: Any) -> Any:
        """
        Executes given request and returns execution result.
        :param obj: request object
        :param kwargs: optional extra arguments
        :return: request execution result
        """
        ...
