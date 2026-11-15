import inspect
import sys
from collections.abc import Sequence
from typing import Annotated

import pytest

from mediator.utils.inspection import CallableArg, CallableDetails, CallableInspector


class X:
    pass


def _check_arg(
    args: Sequence[CallableArg],
    names: Sequence[str] = ("x", "other"),
    types: Sequence[type | None] = (X, int),
    positionals: Sequence[bool] = (True, True),
):
    assert len(args) == len(names)
    for arg, name in zip(args, names, strict=False):
        assert arg.name == name
    for arg, type_ in zip(args, types, strict=False):
        assert arg.type == type_
    for arg, is_positional in zip(args, positionals, strict=False):
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

    # noinspection PyUnusedLocal
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
        assert details.return_type is str
        _check_arg(details.args, types=[X, int])


# noinspection PyUnusedLocal
async def a(x: X, other: int) -> X:
    return x


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
    ("fn", "test_fn"),
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


# noinspection PyUnusedLocal
async def unresolvable_a(x: X, other: "Missing") -> "X":  # type: ignore[name-defined]  # noqa: F821
    return x


# noinspection PyUnusedLocal
async def unresolvable_b(x: "X", other: "inspect.Missing"):  # type: ignore[name-defined]
    pass


# noinspection PyUnusedLocal
async def unresolvable_c(x: 'Annotated[X, "meta"]', other: "Missing"):  # type: ignore[name-defined]  # noqa: F821
    pass


@pytest.mark.parametrize("fn", [unresolvable_a, unresolvable_b, unresolvable_c])
def test_callable_inspector_unresolvable_annotation(fn):
    details = CallableInspector.inspect(fn)
    _check_arg(details.args, types=[X, None])


def test_callable_inspector_unresolvable_return_annotation():
    assert CallableInspector.inspect(unresolvable_a).return_type is X


@pytest.mark.skipif(
    sys.version_info < (3, 14), reason="requires deferred evaluation of annotations"
)
def test_callable_inspector_unresolvable_deferred_annotation():
    namespace = {"X": X}
    exec("async def fn(x: X, other: Missing): pass", namespace)
    details = CallableInspector.inspect(namespace["fn"])
    _check_arg(details.args, types=[X, None])
