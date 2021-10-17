from dataclasses import dataclass, field
from typing import Dict, List, Optional, Type, Union


class MappablePolicy:
    """
    Base class for policy - handler factory input specification.
    """

    def replace_map(self, policy: "MappablePolicy") -> "MappablePolicy":
        """
        Maps this policy into new one, patching internals by given policy.
        :param policy: policy to patch internals
        :return: new policy that is current one with replaced values form given one
        """
        return self


@dataclass
class CallableHandlerPolicy(MappablePolicy):
    """
    Callable handler policy.

    Specification or recipe how to inspect callable object
    and how should be built handler that invokes it.
    """

    # subject arg is to provide explicit primary argument name
    subject_arg: Optional[str] = None
    # arg map can be used for action args names to callable args names mapping
    arg_map: Dict[str, str] = field(default_factory=dict)
    # force fill all action arguments into callable or only ones defined in signature
    arg_strict: bool = False

    @property
    def subject_as_keyword(self):
        """
        Should primary argument provided as a keyword arg.
        :return: True when according to policy primary argument
        will be always provided as keyword arg, False otherwise
        """
        return bool(self.subject_arg)

    def replace_map(self, policy: "MappablePolicy") -> "CallableHandlerPolicy":
        """
        Maps this policy into new one, patching internals by given policy.
        :param policy: policy to patch internals
        :return: new policy that is current one with replaced values form given one
        """
        if isinstance(policy, CallableHandlerPolicy):
            return policy
        else:
            return self


@dataclass
class MethodHandlerPolicy(MappablePolicy):
    """
    Method handler policy.

    Specification or recipe how to inspect object method
    and how should be built handler that invokes it.
    """

    # attribute name to inspect
    name: str
    # attribute value callable handler policy
    policy: CallableHandlerPolicy = field(default_factory=CallableHandlerPolicy)
    # optional object type check (as be one of provided type sequence)
    subtype_of: List[Type] = field(default_factory=list)

    @property
    def precises_type(self) -> bool:
        """
        Is object type checking performed.
        :return: True when corresponding handler factory checks object type,
        False when no object type check is performed
        """
        return bool(self.subtype_of)

    def replace_map(self, policy: "MappablePolicy") -> "MethodHandlerPolicy":
        """
        Maps this policy into new one, patching internals by given policy.
        :param policy: policy to patch internals
        :return: new policy that is current one with replaced values form given one
        """
        if isinstance(policy, CallableHandlerPolicy):
            return MethodHandlerPolicy(
                name=self.name, policy=policy, subtype_of=self.subtype_of
            )
        elif isinstance(policy, MethodHandlerPolicy):
            return policy
        else:
            return self


PolicyType = Union[CallableHandlerPolicy, MethodHandlerPolicy, MappablePolicy]
