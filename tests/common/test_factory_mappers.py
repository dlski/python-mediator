import pytest

from mediator.common.factory import (
    CallableHandlerFactory,
    CallableHandlerPolicy,
    DefaultHandlerFactoryMapper,
    MethodHandlerFactory,
    MethodHandlerPolicy,
)


@pytest.mark.parametrize(
    "policy, factory_type",
    [
        (CallableHandlerPolicy(), CallableHandlerFactory),
        (MethodHandlerPolicy(name="method"), MethodHandlerFactory),
    ],
)
def test_default_handler_factory_mapper(policy, factory_type):
    mapper = DefaultHandlerFactoryMapper()
    factory = mapper.map(policy)
    assert isinstance(factory, factory_type)


def test_type_handler_factory_mapper_error():
    mapper = DefaultHandlerFactoryMapper()
    with pytest.raises(TypeError):
        mapper.map(object())
