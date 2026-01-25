import os

import numpy as np
import pytest

from qmath.func.fbe import CosFbe, Log2Fbe, SinFbe
from qmath.utils.test_utils import QPUTestHelper

RUN_SLOW_TESTS = os.getenv("RUN_SLOW_TESTS") == "1"


def test_cos():
    qpu_helper = QPUTestHelper(num_inputs=1, num_qubits=500, qubits_per_reg=7, radix=5)
    qs_x = qpu_helper.inputs[0]
    op = CosFbe(result_radix=28)
    op.compute(qs_x)
    result = op.get_result_qreg()
    qpu_helper.record_op(op.get_result_qreg())

    for x in np.linspace(-1, 1, 2**6 + 1):
        result = qpu_helper.apply_op([x])
        expected = np.cos(np.pi * x)
        assert abs(result - expected) < 1e-4


def test_sin():
    qpu_helper = QPUTestHelper(num_inputs=1, num_qubits=500, qubits_per_reg=7, radix=5)
    qs_x = qpu_helper.inputs[0]
    op = SinFbe(result_radix=28)
    op.compute(qs_x)
    result = op.get_result_qreg()
    qpu_helper.record_op(op.get_result_qreg())

    for x in np.linspace(-1, 1, 2**6 + 1):
        result = qpu_helper.apply_op([x])
        expected = np.sin(np.pi * x)
        assert abs(result - expected) < 1e-4


@pytest.mark.skipif(not RUN_SLOW_TESTS, reason="slow test")
def test_log2():
    qpu_helper = QPUTestHelper(num_inputs=1, num_qubits=1000, qubits_per_reg=30, radix=24)
    qs_x = qpu_helper.inputs[0]
    op = Log2Fbe(result_radix=11)
    op.compute(qs_x)
    result = op.get_result_qreg()
    qpu_helper.record_op(op.get_result_qreg())

    x_range = list(np.linspace(1, 2, 21)) + [1e-5, 1e-3, 0.5, 3, 4, 10, 20]
    for x in x_range:
        result = qpu_helper.apply_op([x])
        expected = np.log2(x)
        assert abs(result - expected) < 2e-3
