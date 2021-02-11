from typing import Optional, Sequence, Type

import pytest

from mediator.utils.inspection import CallableArg, CallableDetails, CallableInspector


class X:
    pass


def _check_arg(
    args: Sequence[CallableArg],
    names: Sequence[str] = ("x", "other"),
    types: Sequence[Optional[Type]] = (X, int),
    positionals: Sequence[bool] = (True, True),
):
    assert len(args) == len(names)
    for arg, name in zip(args, names):
        assert arg.name == name
    for arg, type_ in zip(args, types):
        assert arg.type == type_
    for arg, is_positional in zip(args, positionals):
        assert arg.is_positional == is_positional


class Methods:
    def a(self, x: X, other: int):
        pass

    @staticmethod
    def a_check(details: CallableDetails):
        assert details.is_method
        assert not details.is_async
        _check_arg(details.args, types=[X, int])

    def b(self, x: "X", *, other: int):
        pass

    @staticmethod
    def b_check(details: CallableDetails):
        assert details.is_method
        assert not details.is_async
        _check_arg(details.args, types=[X, int], positionals=[True, False])

    @classmethod
    async def c(cls, *, x: X, other: int):
        pass

    @staticmethod
    def c_check(details: CallableDetails):
        assert details.is_method
        assert details.is_async
        _check_arg(details.args, types=[X, int], positionals=[False, False])

    @staticmethod
    async def d(x: "X", other: "int") -> "X":
        return x

    @staticmethod
    def d_check(details: CallableDetails):
        assert not details.is_method
        assert details.is_routine
        assert details.is_async
        assert details.return_type == X
        _check_arg(details.args, types=[X, int])

    def e(self, x, other):
        pass

    @staticmethod
    def e_check(details: CallableDetails):
        assert details.is_method
        assert not details.is_async
        assert details.return_type is None
        _check_arg(details.args, types=[None, None])

    def f(self, x: X, other: int, *args, **kwargs):
        pass

    @staticmethod
    def f_check(details: CallableDetails):
        assert details.is_method
        assert not details.is_async
        assert details.return_type is None
        _check_arg(details.args)

    async def __call__(self, x: "X", other: int) -> str:
        return ""

    @staticmethod
    def call_check(details: CallableDetails):
        assert not details.is_method
        assert not details.is_routine
        assert details.is_async
        assert details.return_type == str
        _check_arg(details.args, types=[X, int])


# noinspection PyUnusedLocal
async def a(x: X, other: int) -> X:
    pass


def a_check(details: CallableDetails):
    assert not details.is_method
    assert details.is_async
    assert details.return_type == X
    _check_arg(details.args, types=[X, int])


# noinspection PyUnusedLocal
def b(*, x: X, other):
    pass


def b_check(details: CallableDetails):
    assert not details.is_method
    assert not details.is_async
    assert details.return_type is None
    _check_arg(details.args, types=[X, None], positionals=[False, False])


@pytest.mark.parametrize(
    "fn, test_fn",
    [
        (Methods().a, Methods.a_check),
        (Methods().b, Methods.b_check),
        (Methods.c, Methods.c_check),
        (Methods.d, Methods.d_check),
        (Methods().e, Methods.e_check),
        (Methods().f, Methods.f_check),
        (Methods(), Methods.call_check),
        (a, a_check),
        (b, b_check),
    ],
)
def test_callable_inspector(fn, test_fn):
    result = CallableInspector.inspect(fn)
    test_fn(result)
