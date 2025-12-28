from qmath.utils.re_utils import re_numeric_fixed_point, re_symbolic_fixed_point, verify_re
from qmath.func.common import Negate


def test_re_negate():
    op = Negate()
    re_symbolic = re_symbolic_fixed_point(op, n_inputs=1)
    re_numeric = lambda assgn: re_numeric_fixed_point(op, assgn, n_inputs=1)
    for n, radix in [(5, 0), (5, 5), (8, 8), (10, 5)]:
        verify_re(re_symbolic, re_numeric, {"n": n, "radix": radix}, no_fail=True)


# TODO: Add RE test for Abs, Subtract, MultiplyAdd.
