"""Quantum algorithms for evaluating polynomials and polynomial approximations."""

import os
import random

import numpy as np
import pytest
from psiqworkbench import QPU, QFixed
from psiqworkbench.filter_presets import BIT_DEFAULT

from qmath.poly import HornerScheme
from qmath.utils.test_utils import QPURecorder

RUN_SLOW_TESTS = os.getenv("RUN_SLOW_TESTS") == "1"


@pytest.mark.parametrize("coefs", [[2], [-2, 3.5], [3.5, 2.5, -1]])
def test_horner_linear(coefs: list[float]):
    qpu = QPU(filters=BIT_DEFAULT)
    qpu.reset(100)
    hs = HornerScheme(coefs)
    qx = QFixed(8, name="qx", radix=4, qpu=qpu)
    x = 1.25
    qx.write(x)
    with hs.computed(qx):
        result = hs.get_result_qreg().read()
    assert result == np.polyval(coefs[::-1], x)


@pytest.mark.skipif(not RUN_SLOW_TESTS, reason="slow test")
def test_horner_random():
    qpu = QPU(filters=BIT_DEFAULT)
    qpu.reset(500)
    coefs = [5.1, -4.2, 0.8]
    q_x = QFixed(30, name="x", radix=16, qpu=qpu)
    rec = QPURecorder(qpu)
    hs = HornerScheme(coefs)
    hs.compute(q_x)
    q_result = hs.get_result_qreg()
    rec.record_computation()

    num_trials = 2

    for _ in range(num_trials):
        x = -10 + 20 * random.random()
        rec.restore_initial_state()
        q_x.write(x)
        rec.apply_computation()
        result = q_result.read()
        expected = sum(k * x**i for i, k in enumerate(coefs))
        assert np.isclose(result, expected, atol=1e-3)
