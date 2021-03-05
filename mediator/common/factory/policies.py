from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type, Union


class MappablePolicy:
    def replace_map(self, policy: Any) -> "MappablePolicy":
        return self


@dataclass
class CallableHandlerPolicy(MappablePolicy):
    subject_arg: Optional[str] = None
    arg_map: Dict[str, str] = field(default_factory=dict)
    arg_strict: bool = False

    @property
    def subject_as_keyword(self):
        return bool(self.subject_arg)

    def replace_map(self, policy: Any) -> "CallableHandlerPolicy":
        if isinstance(policy, CallableHandlerPolicy):
            return policy
        else:
            return self


@dataclass
class MethodHandlerPolicy(MappablePolicy):
    name: str
    policy: CallableHandlerPolicy = field(default_factory=CallableHandlerPolicy)
    subtype_of: List[Type] = field(default_factory=list)

    @property
    def precises_type(self) -> bool:
        return bool(self.subtype_of)

    def replace_map(self, policy: Any) -> "MethodHandlerPolicy":
        if isinstance(policy, CallableHandlerPolicy):
            return MethodHandlerPolicy(
                name=self.name, policy=policy, subtype_of=self.subtype_of
            )
        elif isinstance(policy, MethodHandlerPolicy):
            return policy
        else:
            return self


PolicyType = Union[CallableHandlerPolicy, MethodHandlerPolicy]
