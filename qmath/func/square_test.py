import random

import pytest
from psiqworkbench import QPU, QFixed
from psiqworkbench.filter_presets import BIT_DEFAULT

from qmath.func.square import Square, SquareOptimized
from qmath.utils.test_utils import QPUTestHelper


@pytest.mark.smoke
def test_square():
    qpu = QPU(filters=BIT_DEFAULT)
    qpu.reset(100)
    qs_x = QFixed(6, name="x", radix=3, qpu=qpu)
    qs_y = QFixed(6, name="x", radix=3, qpu=qpu)
    qs_x.write(1.5)
    Square().compute(qs_x, qs_y)
    assert qs_y.read() == 2.25


@pytest.mark.smoke
def test_square_optimzied():
    qpu = QPU(filters=BIT_DEFAULT)
    qpu.reset(100)
    qs_x = QFixed(6, name="x", radix=3, qpu=qpu)
    qs_y = QFixed(6, name="x", radix=3, qpu=qpu)
    qs_x.write(1.5)
    SquareOptimized().compute(qs_x, qs_y)
    assert qs_y.read() == 2.25


@pytest.mark.slow
def test_square_optimized_random_high_precision():
    qpu_helper = QPUTestHelper(num_qubits=500, qubits_per_reg=51, radix=41, num_inputs=2)
    q_x, q_ans = qpu_helper.inputs
    SquareOptimized().compute(q_x, q_ans)
    qpu_helper.record_op(q_ans)

    for _ in range(50):
        x = -10 + 20 * random.random()
        result = qpu_helper.apply_op([x, 0], check_no_side_effect=True)
        assert abs(result - x**2) < 1e-11
