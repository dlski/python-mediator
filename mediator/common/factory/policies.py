from dataclasses import dataclass, field
from typing import Dict, List, Optional, Type, Union


class CallableHandlerPolicyOwner:
    def callable(self) -> "CallableHandlerPolicy":
        raise NotImplementedError

    def callable_create(
        self, new: "CallableHandlerPolicy"
    ) -> "CallableHandlerPolicyOwner":
        raise NotImplementedError


@dataclass
class CallableHandlerPolicy(CallableHandlerPolicyOwner):
    subject_arg: Optional[str] = None
    arg_map: Dict[str, str] = field(default_factory=dict)

    @property
    def subject_as_keyword(self):
        return bool(self.subject_arg)

    def callable(self):
        return self

    @staticmethod
    def callable_create(new: "CallableHandlerPolicy"):
        return new


@dataclass
class MethodHandlerPolicy(CallableHandlerPolicyOwner):
    name: str
    policy: CallableHandlerPolicy = field(default_factory=CallableHandlerPolicy)
    subtype_of: List[Type] = field(default_factory=list)

    @property
    def precises_type(self) -> bool:
        return bool(self.subtype_of)

    def callable(self) -> CallableHandlerPolicy:
        return self.policy

    def callable_create(self, new: CallableHandlerPolicy):
        return MethodHandlerPolicy(
            name=self.name,
            policy=new,
            subtype_of=self.subtype_of,
        )


PolicyType = Union[CallableHandlerPolicy, MethodHandlerPolicy]
