import random

from qmath.add import Increment
from qmath.utils.test_utils import QPUTestHelper


def test_increment():
    n = 10

    for _ in range(5):
        y = random.randint(-(2 ** (n - 1)), 2 ** (n - 1) - 1)
        qpu_helper = QPUTestHelper(num_inputs=1, num_qubits=2 * n, qubits_per_reg=n, radix=0)
        qs_x = qpu_helper.inputs[0]
        Increment().compute(qs_x, y)
        qpu_helper.record_op(qs_x)

        for _ in range(5):
            x = random.randint(-(2 ** (n - 1)), 2 ** (n - 1) - 1)
            result = qpu_helper.apply_op([x])
            expected = x + y
            assert (result - expected) % (2**n) == 0
