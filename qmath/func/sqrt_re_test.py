from qmath.func.sqrt import Sqrt
from qmath.utils.re_utils import re_numeric_fixed_point, re_symbolic_fixed_point, verify_re
import pytest


@pytest.mark.re
@pytest.mark.parametrize("half_arg", [False, True])
def test_re_sqrt_fast(half_arg: bool):
    op = Sqrt(half_arg=half_arg)
    re_symbolic = re_symbolic_fixed_point(op)
    re_numeric = lambda assgn: re_numeric_fixed_point(op, assgn)
    verify_re(re_symbolic, re_numeric, {"n": 5, "radix": 1})


@pytest.mark.re
@pytest.mark.slow
@pytest.mark.parametrize("half_arg", [False, True])
def test_re_sqrt(half_arg: bool):
    op = Sqrt(half_arg=half_arg)
    re_symbolic = re_symbolic_fixed_point(op)
    re_numeric = lambda assgn: re_numeric_fixed_point(op, assgn)
    for n in [5, 6, 7, 20, 21]:
        for radix in [0, 1, 2, 5]:
            verify_re(re_symbolic, re_numeric, {"n": n, "radix": radix})
