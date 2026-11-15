import asyncio
import logging
from collections.abc import Callable, Sequence
from typing import Protocol

from mediator.common.types import ActionCallType, ActionSubject

logger = logging.getLogger(__name__)

EventErrorHandler = Callable[[ActionSubject, Exception], object]


class EventDispatcher(Protocol):
    """
    Event dispatcher.

    Strategy that decides how event handlers are run when event is published.
    """

    async def dispatch(
        self, calls: Sequence[ActionCallType], action: ActionSubject
    ) -> None:
        """
        Runs all given event handler calls with given event action.
        :param calls: event handler calls to run (may be empty)
        :param action: event action to be processed
        """
        ...

    async def drain(self) -> None:
        """
        Waits until all event handler calls started by this dispatcher are finished.
        """
        ...


class AwaitingEventDispatcher:
    """
    Awaiting event dispatcher.

    Runs event handlers concurrently and waits until all of them are finished,
    so event is fully processed when publishing returns.
    Failure of one handler does not stop the other ones.
    """

    async def dispatch(
        self, calls: Sequence[ActionCallType], action: ActionSubject
    ) -> None:
        """
        Runs all given event handler calls and waits for them.
        :param calls: event handler calls to run (may be empty)
        :param action: event action to be processed
        :raises ExceptionGroup: with errors of all failed event handlers
        """
        results = await asyncio.gather(
            *(call(action) for call in calls), return_exceptions=True
        )
        errors = [result for result in results if isinstance(result, Exception)]
        if errors:
            raise ExceptionGroup(
                f"Event {type(action.subject).__qualname__} handlers failed", errors
            )

    async def drain(self) -> None:
        """
        Returns immediately: every dispatch waits for its event handlers.
        """


class BackgroundEventDispatcher:
    """
    Background event dispatcher.

    Runs every event handler as separate background asyncio task,
    so publishing returns before event is processed.
    Event handler failures are passed to error handler.
    """

    def __init__(self, on_error: EventErrorHandler | None = None) -> None:
        """
        Initializes background event dispatcher.
        :param on_error: (optional) callable invoked
        with event action and error raised by its handler;
        by default errors are logged using `mediator.event.dispatch` logger
        """
        self._on_error = on_error if on_error is not None else _log_error
        self._tasks: set[asyncio.Task[None]] = set()

    async def dispatch(
        self, calls: Sequence[ActionCallType], action: ActionSubject
    ) -> None:
        """
        Schedules all given event handler calls as background tasks.
        :param calls: event handler calls to run (may be empty)
        :param action: event action to be processed
        """
        for call in calls:
            task = asyncio.create_task(self._run(call, action))
            # event loop keeps only weak references to tasks
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)

    async def drain(self) -> None:
        """
        Waits until all scheduled event handler calls are finished,
        including ones scheduled in meantime (i.e. by running event handlers).
        """
        while self._tasks:
            await asyncio.wait(tuple(self._tasks))

    async def _run(self, call: ActionCallType, action: ActionSubject) -> None:
        """
        Runs single event handler call and reports its failure.
        :param call: event handler call to run
        :param action: event action to be processed
        """
        try:
            await call(action)
        except Exception as error:
            self._on_error(action, error)


def _log_error(action: ActionSubject, error: Exception) -> None:
    """
    Default background event handler error handler - logs given error.
    :param action: event action that was processed
    :param error: error raised by event handler
    """
    logger.error(
        "Event %s handler failed", type(action.subject).__qualname__, exc_info=error
    )
