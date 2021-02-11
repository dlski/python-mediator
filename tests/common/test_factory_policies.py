from mediator.common.factory import CallableHandlerPolicy, MethodHandlerPolicy


def test_callable_handler_policy():
    policy = CallableHandlerPolicy()
    assert not policy.subject_as_keyword
    assert policy.callable() is policy

    second_policy = CallableHandlerPolicy()
    assert policy.callable_create(second_policy) is second_policy

    policy = CallableHandlerPolicy(subject_arg="test")
    assert policy.subject_as_keyword


def test_method_handler_policy():
    policy = MethodHandlerPolicy(name="test", subtype_of=[str])
    assert policy.precises_type
    assert policy.callable() is policy.policy

    callable_policy = CallableHandlerPolicy()
    new_policy = policy.callable_create(callable_policy)
    assert isinstance(new_policy, MethodHandlerPolicy)
    assert new_policy.callable() is callable_policy
    assert new_policy.name == policy.name
    assert [*new_policy.subtype_of] == [*policy.subtype_of]

    policy = MethodHandlerPolicy(name="test")
    assert not policy.precises_type
