import random

from qmath.func.common import AbsInPlace, Subtract, MultiplyConstAdd
from qmath.utils.test_utils import QPUTestHelper


def test_abs():
    qpu_helper = QPUTestHelper(num_inputs=1, num_qubits=10, qubits_per_reg=5, radix=2)
    qs_x = qpu_helper.inputs[0]
    AbsInPlace().compute(qs_x)
    qpu_helper.record_op(qs_x)

    for x in [-1.25, -1.0, 0.0, 2.5]:
        assert qpu_helper.apply_op([x]) == abs(x)


def test_subtract():
    qpu_helper = QPUTestHelper(num_inputs=2, num_qubits=200, qubits_per_reg=40, radix=30)
    qs_x, qs_y = qpu_helper.inputs
    Subtract().compute(qs_x, qs_y)
    qpu_helper.record_op(qs_x)

    for _ in range(10):
        x = -100 + 200 * random.random()
        y = -100 + 200 * random.random()
        result = qpu_helper.apply_op([x, y])
        expected = x - y
        assert abs(result - expected) < 1e-9


def test_multiply_const_add():
    for y in [-11.25, 0, 1.5, 10.3]:
        qpu_helper = QPUTestHelper(num_inputs=2, num_qubits=200, qubits_per_reg=25, radix=15)
        qs_x, qs_z = qpu_helper.inputs
        MultiplyConstAdd(y).compute(qs_z, qs_x)
        qpu_helper.record_op(qs_z)

        for x in [-10, 5.5, 0, 10.125]:
            result = qpu_helper.apply_op([x, 0])
            expected = x * y
            assert abs(result - expected) < 1e-4
