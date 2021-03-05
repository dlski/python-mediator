from typing import Any

from mediator.common.factory.base import HandlerFactory
from mediator.common.factory.policies import CallableHandlerPolicy, MethodHandlerPolicy
from mediator.common.factory.utils import (
    CallableAttributeDetails,
    CallableObjDetails,
    DirectHandlerCreate,
    HandlerSubjectArgGet,
)
from mediator.common.handler import Handler


class CallableHandlerFactory(HandlerFactory):
    def __init__(self, policy: CallableHandlerPolicy):
        self._obj_details = CallableObjDetails()
        self._arg_get = HandlerSubjectArgGet(name=policy.subject_arg)
        self._handler_create = DirectHandlerCreate(
            subject_as_keyword=policy.subject_as_keyword,
            arg_map=policy.arg_map,
            arg_strict=policy.arg_strict,
        )

    def create(self, obj: Any) -> Handler:
        details = self._obj_details(obj)
        arg = self._arg_get(details)
        return self._handler_create(details=details, arg=arg, obj=obj)


class MethodHandlerFactory(HandlerFactory):
    def __init__(self, policy: MethodHandlerPolicy):
        self._attribute_details = CallableAttributeDetails(
            name=policy.name, owner_subtype_of=policy.subtype_of
        )
        callable_policy = policy.policy
        self._arg_get = HandlerSubjectArgGet(name=callable_policy.subject_arg)
        self._handler_create = DirectHandlerCreate(
            subject_as_keyword=callable_policy.subject_as_keyword,
            arg_map=callable_policy.arg_map,
            arg_strict=callable_policy.arg_strict,
        )

    def create(self, obj: Any) -> Handler:
        details = self._attribute_details(obj)
        arg = self._arg_get(details)
        return self._handler_create(details=details, arg=arg, obj=obj)
