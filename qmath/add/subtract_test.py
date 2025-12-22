import random

from qmath.add import Subtract
from qmath.utils.test_utils import QPUTestHelper


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
        print(x, y, result, expected)
        assert abs(result - expected) < 1e-9
