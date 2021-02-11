from typing import Any, Callable, Sequence

import pytest

from mediator.common.factory import (
    CallableHandlerFactory,
    CallableHandlerPolicy,
    ConfigHandlerFactoryCascadeError,
    HandlerFactoryCascade,
    HandlerFactoryCascadeError,
    HandlerFactoryError,
    IncompatibleHandlerFactoryCascadeError,
    IncompatibleHandlerFactoryError,
    InspectionHandlerFactoryCascadeError,
    MethodHandlerFactory,
    MethodHandlerPolicy,
    PolicyType,
)
from mediator.common.handler import Handler
from mediator.common.types import ActionSubject


class _A:
    # noinspection PyMethodMayBeStatic
    async def method(self, arg: str):
        return arg

    # noinspection PyMethodMayBeStatic
    def method_no_type(self, arg):
        return arg


async def _check_handler_works(handler: Handler):
    result = await handler(ActionSubject(subject="test", inject={}))
    assert result.result == "test"


@pytest.mark.parametrize("obj", [_A(), _A().method])
@pytest.mark.asyncio
async def test_handler_factory_cascade_success(obj):
    cascade = HandlerFactoryCascade(
        policies=[CallableHandlerPolicy(), MethodHandlerPolicy(name="method")]
    )
    handler = cascade(obj)
    await _check_handler_works(handler)


@pytest.mark.asyncio
async def test_handler_factory_cascade_replace():
    cascade = HandlerFactoryCascade(policies=[CallableHandlerPolicy()])
    obj = _A()

    with pytest.raises(IncompatibleHandlerFactoryCascadeError):
        cascade(obj)

    cascade = cascade.replace(policies=[MethodHandlerPolicy(name="method")])
    handler = cascade(obj)
    await _check_handler_works(handler)


def _check_config_error(error: HandlerFactoryCascadeError):
    assert isinstance(error, ConfigHandlerFactoryCascadeError)


def _check_inspect_error(error: HandlerFactoryCascadeError):
    assert isinstance(error, InspectionHandlerFactoryCascadeError)
    assert isinstance(error.factory, MethodHandlerFactory)
    assert isinstance(error.__cause__, HandlerFactoryError)


def _check_incompatible_error(error: HandlerFactoryCascadeError):
    assert isinstance(error, IncompatibleHandlerFactoryCascadeError)
    factory_errors = error.factory_errors
    assert len(factory_errors) == 2
    for (factory, error), factory_type in zip(
        factory_errors, [MethodHandlerFactory, CallableHandlerFactory]
    ):
        assert isinstance(factory, factory_type)
        assert isinstance(error, IncompatibleHandlerFactoryError)


@pytest.mark.parametrize(
    "obj, policies, error_check",
    [
        (None, [], _check_config_error),
        (_A(), [MethodHandlerPolicy(name="method_no_type")], _check_inspect_error),
        (
            _A(),
            [MethodHandlerPolicy(name="non_existing"), CallableHandlerPolicy()],
            _check_incompatible_error,
        ),
    ],
)
def test_handler_factory_cascade_error(
    obj,
    policies: Sequence[PolicyType],
    error_check: Callable[[HandlerFactoryCascadeError], Any],
):
    with pytest.raises(HandlerFactoryCascadeError) as e:
        cascade = HandlerFactoryCascade(policies=policies)
        cascade(obj)
    error_check(e.value)
