import os
import random

import numpy as np
import pytest
from psiqworkbench import QPU, QFixed, QUInt

from qmath.poly import WritePieceNumber


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
