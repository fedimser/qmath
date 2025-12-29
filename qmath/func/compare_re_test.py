from qmath.func.compare import CompareConstGT
from qmath.utils.re_utils import re_symbolic_fixed_point, re_numeric_fixed_point, verify_re
import pytest


@pytest.mark.parametrize("c", [5.0, 7.25, 7 / 3])
def test_re_compare(c: float):
    op = CompareConstGT(c)
    re_symbolic = re_symbolic_fixed_point(op)
    re_numeric = lambda assgn: re_numeric_fixed_point(op, assgn)
    for n, radix in [(10, 6), (20, 6), (20, 10), (20, 16), (30, 10), (30, 20)]:
        verify_re(re_symbolic, re_numeric, {"n": n, "radix": radix})
