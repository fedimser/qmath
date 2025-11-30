"""Quantum algorithms for evaluating polynomials and polynomial approximations."""

import random

import numpy as np
from psiqworkbench import QPU, QFixed

from qmath.poly import HornerScheme


def test_horner():
    qpu = QPU(filters=[">>64bit>>", ">>bit-sim>>"])
    qpu.reset(500)
    coefs = [5.1, -4.2, 0.8]
    num_trials = 1

    for _ in range(num_trials):
        x = -10 + 20 * random.random()
        hs = HornerScheme(coefs)
        qx = QFixed(30, name="qx", radix=16, qpu=qpu)
        qx.write(x)
        hs.compute(qx)
        result = hs.get_result_qreg().read()
        hs.uncompute()
        expected = sum(k * x**i for i, k in enumerate(coefs))
        assert np.isclose(result, expected, atol=1e-3)
