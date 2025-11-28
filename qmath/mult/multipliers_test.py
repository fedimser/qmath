import random

import pytest
from psiqworkbench import QPU, QUInt

from qmath.mult import JHHAMultipler, MCTMultipler, Multiplier


def _check_multiplier(multiplier: Multiplier, num_bits, num_trials=5):
    qc = QPU(filters=[">>64bit>>", ">>bit-sim>>"])
    qc.reset(4 * num_bits + 1)

    a = QUInt(num_bits, "a", qc)
    b = QUInt(num_bits, "b", qc)
    c = QUInt(2 * num_bits, "c", qc)

    for _ in range(num_trials):
        x = random.randint(0, 2**num_bits - 1)
        y = random.randint(0, 2**num_bits - 1)
        a.write(x)
        b.write(y)
        c.write(0)
        multiplier.compute(a, b, c)
        assert c.read() == x * y


@pytest.mark.parametrize("num_bits", [1, 2, 5, 10])
def test_mct_multiplier(num_bits: int):
    _check_multiplier(MCTMultipler(), num_bits)


@pytest.mark.parametrize("num_bits", [1, 2, 5, 10])
def test_jhha_multiplier(num_bits: int):
    _check_multiplier(JHHAMultipler(num_bits), 10)
