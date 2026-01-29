from qmath.func.common import AbsInPlace, Add, Negate, Subtract, MultiplyAdd, AddConst
from qmath.utils.re_utils import re_numeric_fixed_point, re_symbolic_fixed_point, verify_re
import pytest


@pytest.mark.re
def test_re_negate():
    op = Negate()
    re_symbolic = re_symbolic_fixed_point(op, n_inputs=1)
    re_numeric = lambda assgn: re_numeric_fixed_point(op, assgn, n_inputs=1)
    for n, radix in [(2, 0), (2, 1), (5, 0), (5, 5), (8, 8), (10, 5)]:
        verify_re(re_symbolic, re_numeric, {"n": n, "radix": radix})


@pytest.mark.re
def test_re_abs():
    op = AbsInPlace()
    re_symbolic = re_symbolic_fixed_point(op, n_inputs=1)
    re_numeric = lambda assgn: re_numeric_fixed_point(op, assgn, n_inputs=1)
    for n, radix in [(2, 0), (2, 1), (5, 0), (5, 5), (8, 8), (10, 5)]:
        verify_re(re_symbolic, re_numeric, {"n": n, "radix": radix}, av_atol=0.5)


@pytest.mark.re
def test_re_add():
    op = Add()
    re_symbolic = re_symbolic_fixed_point(op, n_inputs=2)
    re_numeric = lambda assgn: re_numeric_fixed_point(op, assgn, n_inputs=2)
    for n, radix in [(2, 0), (2, 1), (5, 0), (5, 5), (8, 8), (10, 5), (16, 16)]:
        verify_re(re_symbolic, re_numeric, {"n": n, "radix": radix})


@pytest.mark.re
@pytest.mark.parametrize("c", [5 / 3, 6.0, 1.75])
def test_re_add_const(c: float):
    op = AddConst(c)
    re_symbolic = re_symbolic_fixed_point(op)
    re_numeric = lambda assgn: re_numeric_fixed_point(op, assgn)
    for n, radix in [(10, 5), (30, 20), (30, 10)]:
        verify_re(re_symbolic, re_numeric, {"n": n, "radix": radix})


@pytest.mark.re
def test_re_subtract():
    op = Subtract()
    re_symbolic = re_symbolic_fixed_point(op, n_inputs=2)
    re_numeric = lambda assgn: re_numeric_fixed_point(op, assgn, n_inputs=2)
    for n, radix in [(10, 0), (10, 5)]:
        verify_re(re_symbolic, re_numeric, {"n": n, "radix": radix})


@pytest.mark.re
def test_re_multiply_add():
    op = MultiplyAdd()
    re_symbolic = re_symbolic_fixed_point(op, n_inputs=3)
    re_numeric = lambda assgn: re_numeric_fixed_point(op, assgn, n_inputs=3)
    for n, radix in [(4, 1), (4, 2), (4, 3), (5, 1), (5, 4), (10, 1), (10, 9), (16, 8)]:
        verify_re(re_symbolic, re_numeric, {"n": n, "radix": radix}, av_rtol=0.001)
