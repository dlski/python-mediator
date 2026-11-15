from typing import Any

from mediator.common.factory.base import HandlerFactory
from mediator.common.factory.policies import CallableHandlerPolicy, MethodHandlerPolicy
from mediator.common.factory.utils import (
    CallableAttributeDetails,
    CallableHandlerCreate,
    CallableObjDetails,
    HandlerSubjectArgGet,
)
from mediator.common.handler import Handler


class CallableHandlerFactory(HandlerFactory):
    """
    Callable handler factory.

    Factory that produces callable handler directly from callable object.
    """

    def __init__(self, policy: CallableHandlerPolicy):
        """
        Initializes callable handler factory.
        :param policy: policy used as a configuration or specification
        for producing handler object
        """
        self._obj_details = CallableObjDetails()
        self._arg_get = HandlerSubjectArgGet(name=policy.subject_arg)
        self._handler_create = CallableHandlerCreate(
            subject_as_keyword=policy.subject_as_keyword,
            arg_map=policy.arg_map,
            arg_strict=policy.arg_strict,
        )

    def create(self, obj: Any) -> Handler:
        """
        Creates handler directly form callable object.
        :param obj: callable object
        :raises IncompatibleHandlerFactoryError: when callable object is incompatible
        with factory specification
        :raises HandlerFactoryError: when there is failure during object inspection
        :return: handler invoking given callable object
        """
        details = self._obj_details(obj)
        arg = self._arg_get(details)
        return self._handler_create(details=details, arg=arg, obj=obj)


class MethodHandlerFactory(HandlerFactory):
    """
    Method handler factory.

    Factory that produces callable handler from given object attribute
    - in most cases method.
    """

    def __init__(self, policy: MethodHandlerPolicy):
        """
        Initializes method handler factory.
        :param policy: policy used as a configuration or specification
        for producing handler object
        """
        self._attribute_details = CallableAttributeDetails(
            name=policy.name, owner_subtype_of=policy.subtype_of
        )
        callable_policy = policy.policy
        self._arg_get = HandlerSubjectArgGet(name=callable_policy.subject_arg)
        self._handler_create = CallableHandlerCreate(
            subject_as_keyword=callable_policy.subject_as_keyword,
            arg_map=callable_policy.arg_map,
            arg_strict=callable_policy.arg_strict,
        )

    def create(self, obj: Any) -> Handler:
        """
        Creates handler from given object attribute according to specification.
        :param obj: callable object
        :raises IncompatibleHandlerFactoryError: when callable object is incompatible
        with factory specification
        :raises HandlerFactoryError: when there is failure during object inspection
        :return: handler invoking given object callable attribute
        """
        details = self._attribute_details(obj)
        arg = self._arg_get(details)
        return self._handler_create(details=details, arg=arg, obj=obj)
