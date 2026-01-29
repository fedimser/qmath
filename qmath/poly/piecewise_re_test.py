from qmath.poly.piecewise import EvalFunctionPPA
from qmath.utils.re_utils import re_symbolic_fixed_point, re_numeric_fixed_point, verify_re
import numpy as np
import pytest


@pytest.mark.re
def test_re_ppa():
    op = EvalFunctionPPA(lambda x: np.cos(x), interval=[-1, 1], degree=2, error_tol=1e-3)
    re_symbolic = re_symbolic_fixed_point(op, n_inputs=1)
    re_numeric = lambda assgn: re_numeric_fixed_point(op, assgn, n_inputs=1)
    verify_re(re_symbolic, re_numeric, {"n": 10, "radix": 6}, av_rtol=0.015, elbows_rtol=0.01)


@pytest.mark.re
@pytest.mark.slow
def test_re_ppa_slow():
    ops = [
        EvalFunctionPPA(lambda x: np.cos(x), interval=[-1, 1], degree=2, error_tol=1e-3),
        EvalFunctionPPA(lambda x: np.sin(x), interval=[-1, 1], degree=3, error_tol=1e-5),
        EvalFunctionPPA(lambda x: np.sin(x), interval=[-1, 1], degree=3, error_tol=1e-5, is_odd=True),
    ]
    params = [(12, 6), (20, 10), (30, 15)]
    for op in ops:
        re_symbolic = re_symbolic_fixed_point(op, n_inputs=1)
        re_numeric = lambda assgn: re_numeric_fixed_point(op, assgn, n_inputs=1)
        for n, radix in params:
            verify_re(re_symbolic, re_numeric, {"n": n, "radix": radix}, av_rtol=0.015, elbows_rtol=0.01)
