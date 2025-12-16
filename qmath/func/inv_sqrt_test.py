import numpy as np
from psiqworkbench import QPU, QFixed, QUInt
from psiqworkbench.filter_presets import BIT_DEFAULT

from qmath.func.inv_sqrt import _InitialGuess, _NewtonIteration
from qmath.utils.test_utils import QPURecorder
from math import floor, log2
import random


def test_newton_iteration():
    qpu = QPU(filters=BIT_DEFAULT)
    qpu.reset(150)
    q_a = QFixed(15, name="a", radix=9, qpu=qpu)
    q_x0 = QFixed(15, name="x0", radix=9, qpu=qpu)
    q_x1 = QFixed(15, name="x1", radix=9, qpu=qpu)
    rec = QPURecorder(qpu)
    _NewtonIteration().compute(q_x0, q_x1, q_a)
    rec.record_computation()

    for x0 in [-1.25, 0.5]:
        for a in [-5, 6.125]:
            rec.restore_initial_state()
            q_a.write(a)
            q_x0.write(x0)
            rec.apply_computation()
            result = q_x1.read()
            expected = x0 * (1.5 - a * x0**2)
            assert np.isclose(result, expected)


def test_initial_guess():
    qpu = QPU(filters=BIT_DEFAULT)
    qpu.reset(100)
    q_a = QFixed(30, name="a", radix=20, qpu=qpu)
    q_ans = QFixed(30, name="ans", radix=20, qpu=qpu)
    rec = QPURecorder(qpu)
    _InitialGuess().compute(q_a, q_ans)
    rec.record_computation()

    a_range = [2**-17, 2**-16, 0.5, 0.3, 1, 1.5, 2, 10, 100, 511, 511.9]
    a_range += [0.1 + 511 * random.random() for _ in range(10)]
    for a in a_range:
        rec.restore_initial_state()
        q_a.write(a)
        rec.apply_computation()
        result = q_ans.read()
        expected = 2 ** (-(int(floor(log2(a)))) // 2)
        assert result == expected
