import random

from qmath.func.sqrt import Sqrt
from qmath.utils.test_utils import QPUTestHelper
from psiqworkbench.filter_presets import BIT_DEFAULT
from psiqworkbench import QPU, QFixed


def test_sqrt():
    qpu_helper = QPUTestHelper(num_inputs=1, num_qubits=200, qubits_per_reg=50, radix=40)
    qs_x = qpu_helper.inputs[0]
    op = Sqrt()
    op.compute(qs_x)
    qpu_helper.record_op(op.get_result_qreg())

    for x in [0, 1e-3, 0.15, 0.2, 0.5, 1, 2, 3, 10, 100, 500]:
        result = qpu_helper.apply_op([x])
        assert abs(result - x**0.5) < 1e-6


def test_sqrt_half():
    qpu_helper = QPUTestHelper(num_inputs=1, num_qubits=200, qubits_per_reg=20, radix=15)
    qs_x = qpu_helper.inputs[0]
    op = Sqrt(half_arg=True)
    op.compute(qs_x)
    result = op.get_result_qreg()
    qpu_helper.record_op(op.get_result_qreg())

    for x in [0, 0.5, 1, 2, 8]:
        result = qpu_helper.apply_op([x])
        expected = (x / 2) ** 0.5
        assert abs(result - expected) < 1e-4


def test_sqrt_padding():
    for num_qubits, r in [(9, 4), (9, 5), (10, 4), (10, 5)]:
        qpu = QPU(filters=BIT_DEFAULT)
        qpu.reset(40)
        qx = QFixed(num_qubits, name="x", radix=r, qpu=qpu)
        qx.write(2.25)
        op = Sqrt()
        op.compute(qx)
        result = op.get_result_qreg()
        assert result.num_qubits == num_qubits
        assert result.radix == r
        assert result.read() == 1.5


def test_half_padding():
    for num_qubits, r in [(9, 4), (9, 5), (10, 4), (10, 5)]:
        qpu = QPU(filters=BIT_DEFAULT)
        qpu.reset(40)
        qx = QFixed(num_qubits, name="x", radix=r, qpu=qpu)
        qx.write(4.5)
        op = Sqrt(half_arg=True)
        op.compute(qx)
        result = op.get_result_qreg()
        assert result.num_qubits == num_qubits
        assert result.radix == r
        assert result.read() == 1.5
