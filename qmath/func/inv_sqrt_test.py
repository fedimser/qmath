import random
from math import floor, log2

import numpy as np
import pytest
from psiqworkbench import QFixed

from qmath.func.inv_sqrt import InverseSquareRoot, _InitialGuess, _NewtonIteration
from qmath.utils.test_utils import QPUTestHelper


def test_newton_iteration():
    qpu_helper = QPUTestHelper(num_qubits=150, qubits_per_reg=15, radix=9, num_inputs=2)
    q_a, q_x0 = qpu_helper.inputs
    q_x1 = QFixed(15, name="x1", radix=9, qpu=qpu_helper.qpu)
    _NewtonIteration().compute(q_x0, q_x1, q_a)
    qpu_helper.record_op(q_x1)

    for x0, a in [(-1.25, -5), (0.5, 6.125), (1, 2)]:
        result = qpu_helper.apply_op([a, x0])
        expected = x0 * (1.5 - a * x0**2)
        assert np.isclose(result, expected)


def test_initial_guess():
    qpu_helper = QPUTestHelper(num_qubits=100, qubits_per_reg=30, radix=20, num_inputs=1)
    q_a = qpu_helper.inputs[0]
    q_ans = QFixed(30, name="ans", radix=20, qpu=qpu_helper.qpu)
    _InitialGuess().compute(q_a, q_ans)
    qpu_helper.record_op(q_ans)

    a_range = [2**-17, 2**-16, 0.5, 0.3, 1, 1.5, 2, 10, 100, 511, 511.9]
    a_range += [0.1 + 511 * random.random() for _ in range(10)]
    for a in a_range:
        result = qpu_helper.apply_op([a])
        expected = 2 ** (-(int(floor(log2(a)))) // 2)
        assert result == expected


@pytest.mark.slow
def test_inverse_square_root_low_precision():
    qpu_helper = QPUTestHelper(num_qubits=400, qubits_per_reg=15, radix=11)
    func = InverseSquareRoot(num_iterations=3)
    func.compute(qpu_helper.inputs[0])
    qpu_helper.record_op(func.get_result_qreg())

    for a in np.linspace(0.25, 5, 100):
        result = qpu_helper.apply_op([a])
        expected = a**-0.5
        assert np.abs(result - expected) < 1e-3
