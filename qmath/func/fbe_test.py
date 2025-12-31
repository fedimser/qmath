from qmath.func.fbe import CosFbe
from qmath.utils.test_utils import QPUTestHelper

import numpy as np


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
