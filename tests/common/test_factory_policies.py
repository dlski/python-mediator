from mediator.common.factory import CallableHandlerPolicy, MethodHandlerPolicy


def test_callable_handler_policy():
    policy = CallableHandlerPolicy()
    assert not policy.subject_as_keyword

    policy = CallableHandlerPolicy(subject_arg="test")
    assert policy.subject_as_keyword

    second_policy = CallableHandlerPolicy()
    assert policy.replace_map(second_policy) is second_policy
    assert policy.replace_map(None) is policy


def test_method_handler_policy():
    policy = MethodHandlerPolicy(name="test", subtype_of=[str])
    assert policy.precises_type

    policy = MethodHandlerPolicy(name="test")
    assert not policy.precises_type

    callable_policy = CallableHandlerPolicy()
    new_policy = policy.replace_map(callable_policy)
    assert isinstance(new_policy, MethodHandlerPolicy)
    assert new_policy.policy is callable_policy
    assert new_policy.name == policy.name
    assert list(new_policy.subtype_of) == list(policy.subtype_of)

    second_policy = MethodHandlerPolicy(name="other")
    assert policy.replace_map(second_policy) is second_policy

    assert policy.replace_map(None) is policy
