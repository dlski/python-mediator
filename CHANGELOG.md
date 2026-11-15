# Changelog

## 0.8.0

Requires Python 3.11 or newer.

### Added
- Type information is shipped with the package (`py.typed`), checked with strict mypy.
- `Request[R]` optional base class - `execute` returns precise result type for it.
- Event dispatchers: `BackgroundEventDispatcher` (default) and `AwaitingEventDispatcher`,
  custom ones can be provided by `LocalEventBus(dispatcher=...)`.
- `LocalEventBus.drain()` waits until background event handlers are finished.
- Handler annotated with union of types (`A | B`) is registered for all of them.
- Main names can be imported directly from `mediator` package.

### Changed
- `LocalEventBus(sync_mode=True)` is replaced by
  `LocalEventBus(dispatcher=AwaitingEventDispatcher())`.
  Handler errors are raised from `publish` as `ExceptionGroup`.
- Background event handler errors are logged (or passed to `on_error` callable)
  instead of being lost.
- Interfaces (`Handler`, `HandlerStore`, `HandlerFactory`, `ModifierFactory`,
  `EventPublish`, `EventPublisher`, `EventSubscriber`, `RequestExecutor`)
  are `typing.Protocol` classes. Inheriting from them still works.
- `ModifierFactory.create(call, *, target)` - target is explicit keyword argument
  instead of being part of `**kwargs`.
- `HandlerFactory.create` and `HandlerFactoryCascade.__call__` return
  sequence of handlers instead of single one.
- `ActionSubject`, `ActionResult`, `HandlerEntry`, policies and inspection records
  are immutable.
- Helper classes of `mediator.common.factory.utils` are replaced by functions.
- `LocalRequestBus.execute` raises `TypeError` instead of `AssertionError`
  when modifier does not return `ActionResult`.
- `mediator.utils.context.AsyncNullContextManager` is removed,
  use `contextlib.nullcontext`.

### Fixed
- Publishing event without handlers failed with `ValueError` in sync mode.
- Background event handler task could be garbage collected before it finished.
- `include()` given one-shot iterator stored handlers but never called them.
- Handler taking subject as keyword argument leaked it
  into extra arguments of other handlers of the same event.
- Annotation that cannot be resolved (i.e. `TYPE_CHECKING` only import)
  on argument other than subject failed handler registration.
