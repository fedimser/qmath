import random

from qmath.uint_arith.add import Increment
from qmath.utils.test_utils import QPUTestHelper


def test_increment():
    n = 10

    for y in [0, 1, 2, 3, 16, 512, 1023]:
        qpu_helper = QPUTestHelper(num_inputs=1, num_qubits=2 * n, qubits_per_reg=n, radix=0)
        qs_x = qpu_helper.inputs[0]
        Increment().compute(qs_x, y)
        qpu_helper.record_op(qs_x)

        for _ in range(5):
            x = random.randint(-(2 ** (n - 1)), 2 ** (n - 1) - 1)
            result = qpu_helper.apply_op([x])
            assert (result - (x + y)) % (2**n) == 0
