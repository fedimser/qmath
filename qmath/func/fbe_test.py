import numpy as np
import pytest
from psiqworkbench import QPU, QFixed, QUFixed
from psiqworkbench.filter_presets import BIT_DEFAULT

from qmath.func.fbe import CosFbe, Log2Fbe, SinFbe, Pow2Segment
from qmath.utils.test_utils import QPUTestHelper


@pytest.mark.smoke
def test_sin_fast():
    qpu = QPU(filters=BIT_DEFAULT)
    qpu.reset(100)
    qs_x = QFixed(5, name="x", radix=3, qpu=qpu)
    qs_x.write(0.5)
    op = SinFbe()
    op.compute(qs_x)
    assert op.get_result_qreg().read() == 1.0  # sin(pi/2)==1.


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


@pytest.mark.slow
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


def test_pow2_segment():
    qpu = QPU(filters=BIT_DEFAULT)
    qpu.reset(200)
    qs_x = QUFixed(3, name="x", radix=3, qpu=qpu)
    qs_x.write(0.625)
    op = Pow2Segment(result_radix=22)
    op.compute(qs_x)
    result = op.get_result_qreg().read()
    assert abs(result - 2**0.625) < 1e-3
