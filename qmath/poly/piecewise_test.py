import os
import random

import numpy as np
import pytest
from psiqworkbench import QPU, QFixed, QUInt

from qmath.poly import WritePieceNumber, EvalPiecewisePolynomial, PiecewisePolynomial, Piece, EvalFunctionPPA

RUN_SLOW_TESTS = os.getenv("RUN_SLOW_TESTS") == "1"


def test_write_piece_number():
    qpu = QPU(filters=[">>64bit>>", ">>bit-sim>>"])
    qpu.reset(30)
    qx = QFixed(10, name="qx", radix=5, qpu=qpu)
    target = QUInt(3, qpu=qpu)
    split_points = [-7.5, -6.5, -2.25, 0, 0.5, 6.0]

    def _check(x, expected_result):
        qx.write(x)
        target.write(0)
        func = WritePieceNumber()
        func.compute(qx, target, split_points)
        assert target.read() == expected_result

    for i, x in enumerate(split_points):
        _check(x - 0.1, i)
        _check(x, i)
        _check(x + 0.1, i + 1)


def test_eval_piecewise_polynomial():
    poly = PiecewisePolynomial(
        [
            Piece(-1, 0, [1, 1, 1, 0]),
            Piece(0, 1.5, [1, -2, -2.5, 0]),
            Piece(1.5, 2.5, [5.875, -3, -5.5, 1]),
        ]
    )
    qpu = QPU(filters=[">>64bit>>", ">>bit-sim>>", ">>buffer>>", ">>capture>>"])
    for x in [-1, 1.5, 2]:
        qpu.reset(150)
        qx = QFixed(8, name="qx", radix=3, qpu=qpu)
        qx.write(x)
        func = EvalPiecewisePolynomial(poly)
        func.compute(qx)
        result = func.get_result_qreg().read()
        assert result == poly.eval(x)


@pytest.mark.skipif(not RUN_SLOW_TESTS, reason="slow test")
def test_eval_sin():
    qpu = QPU(filters=[">>64bit>>", ">>bit-sim>>", ">>buffer>>", ">>capture>>"])
    func = EvalFunctionPPA(np.sin, interval=(-1, 1), degree=3, error_tol=1e-4)

    for x in [0.5, 0.8, 1.0]:
        qpu.reset(500)
        qx = QFixed(20, name="qx", radix=15, qpu=qpu)
        qx.write(x)
        func.compute(qx)
        result = func.get_result_qreg().read()
        assert np.abs(result - np.sin(x)) < 1e-4
