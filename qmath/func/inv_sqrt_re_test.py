from qmath.func.inv_sqrt import _InitialGuess, _NewtonIteration, InverseSquareRoot
from qmath.utils.re_utils import re_symbolic_fixed_point, re_numeric_fixed_point, verify_re
import pytest


@pytest.mark.re
def test_re_initial_guess():
    op = _InitialGuess()
    re_symbolic = re_symbolic_fixed_point(op, n_inputs=2)
    re_numeric = lambda assgn: re_numeric_fixed_point(op, assgn, n_inputs=2)
    for n, radix in [(20, 7), (20, 12), (30, 10), (30, 19)]:
        verify_re(re_symbolic, re_numeric, {"n": n, "radix": radix})


@pytest.mark.re
@pytest.mark.slow
def test_re_newton_iteration():
    op = _NewtonIteration()
    re_symbolic = re_symbolic_fixed_point(op, n_inputs=3)
    re_numeric = lambda assgn: re_numeric_fixed_point(op, assgn, n_inputs=3)
    for n, radix in [(10, 5)]:
        verify_re(re_symbolic, re_numeric, {"n": n, "radix": radix}, av_rtol=0.001)


@pytest.mark.re
@pytest.mark.slow
@pytest.mark.parametrize("num_iterations", [1, 2])
def test_re_inv_sqrt(num_iterations: int):
    op = InverseSquareRoot(num_iterations=num_iterations)
    re_symbolic = re_symbolic_fixed_point(op, n_inputs=1)
    re_numeric = lambda assgn: re_numeric_fixed_point(op, assgn, n_inputs=1, qubits_factor=20)
    test_cases = [(6, 2), (6, 3), (6, 4), (10, 3), (10, 5), (10, 8), (20, 7), (20, 12)]
    for n, radix in test_cases:
        verify_re(re_symbolic, re_numeric, {"n": n, "radix": radix}, av_rtol=0.001)
