import os
import random

import pytest

from qmath.mult import Square
from qmath.utils.test_utils import QPUTestHelper
from psiqworkbench.filter_presets import BIT_DEFAULT
from psiqworkbench import QPU, Qubits, QFixed, QUInt

RUN_SLOW_TESTS = os.getenv("RUN_SLOW_TESTS") == "1"


def test_square_5bit():
    qpu = QPU(filters=BIT_DEFAULT)
    qpu.reset(25)
    q_x = QFixed(5, name="x", radix=2, qpu=qpu)
    q_ans = QFixed(5, name="ans", radix=2, qpu=qpu)
    q_x.write(1.5)
    Square().compute(q_x, q_ans)
    assert q_ans.read() == 2.25


def test_square_8bit():
    qpu = QPU(filters=BIT_DEFAULT)
    qpu.reset(100)
    q_x = QFixed(8, name="x", radix=4, qpu=qpu)
    q_ans = QFixed(8, name="ans", radix=4, qpu=qpu)
    q_x.write(1.5)
    Square().compute(q_x, q_ans)
    assert q_ans.read() == 2.25


def test_square_random():
    qpu_helper = QPUTestHelper(num_qubits=200, qubits_per_reg=26, radix=18, num_inputs=2)
    q_x, q_ans = qpu_helper.inputs
    Square().compute(q_x, q_ans)
    qpu_helper.record_op(q_ans)

    for _ in range(50):
        x = -10 + 20 * random.random()
        result = qpu_helper.apply_op([x, 0], check_no_side_effect=True)
        assert abs(result - x**2) < 1e-4


@pytest.mark.skipif(not RUN_SLOW_TESTS, reason="slow test")
def test_square_random_high_precision():
    qpu_helper = QPUTestHelper(num_qubits=500, qubits_per_reg=51, radix=41, num_inputs=2)
    q_x, q_ans = qpu_helper.inputs
    Square().compute(q_x, q_ans)
    qpu_helper.record_op(q_ans)

    for _ in range(50):
        x = -10 + 20 * random.random()
        result = qpu_helper.apply_op([x, 0], check_no_side_effect=True)
        assert abs(result - x**2) < 1e-11
