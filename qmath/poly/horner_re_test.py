from qmath.poly.horner import HornerScheme
from qmath.utils.re_utils import re_symbolic_fixed_point, re_numeric_fixed_point, verify_re


def test_horner_scheme():
    op = HornerScheme([-1, 2.5])
    re_symbolic = re_symbolic_fixed_point(op, n_inputs=1)
    re_numeric = lambda assgn: re_numeric_fixed_point(op, assgn, n_inputs=1)
    for n, radix in [(10, 5)]:
        verify_re(re_symbolic, re_numeric, {"n": n, "radix": radix}, av_rtol=0.001)
