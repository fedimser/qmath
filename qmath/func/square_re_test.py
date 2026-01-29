from qmath.func.square import Square, SquareOptimized
from qmath.utils.re_utils import re_numeric_fixed_point, re_symbolic_fixed_point, verify_re
import pytest


@pytest.mark.re
def test_re_square():
    op = Square()
    re_symbolic = re_symbolic_fixed_point(op, n_inputs=2)
    re_numeric = lambda assgn: re_numeric_fixed_point(op, assgn, n_inputs=2)
    for n, radix in [(10, 1), (10, 5), (10, 9)]:
        verify_re(re_symbolic, re_numeric, {"n": n, "radix": radix}, av_rtol=0.001)


@pytest.mark.re
@pytest.mark.slow
def test_re_square_optimized():
    op = SquareOptimized()
    re_symbolic = re_symbolic_fixed_point(op, n_inputs=2)
    re_numeric = lambda assgn: re_numeric_fixed_point(op, assgn, n_inputs=2)
    params = [(8, 4), (10, 1), (10, 5), (10, 6), (15, 5)]
    params += [(20, 6), (20, 10), (20, 15), (20, 16), (30, 10), (30, 20), (40, 10), (40, 20)]
    for n, radix in params:
        verify_re(re_symbolic, re_numeric, {"n": n, "radix": radix}, av_rtol=0.01, elbows_rtol=0.01)
