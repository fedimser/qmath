import random

import pytest
from psiqworkbench import QPU, QUInt

from qmath.mult import JHHAMultipler, MCTMultipler, Multiplier
from qmath.mult.cg2019 import schoolbook_multiplication


def _check_multiplier(multiplier: Multiplier, num_bits, num_trials=5):
    qc = QPU(filters=[">>64bit>>", ">>bit-sim>>"])
    qc.reset(1000)#4 * num_bits + 1)

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


def _check_multiplier_set(multiplier: Multiplier, num_bits, x_in : int, y_in: int):
    qc = QPU(filters=[">>64bit>>", ">>bit-sim>>"])
    qc.reset(1000)#4 * num_bits + 1)

    a = QUInt(num_bits, "a", qc)
    b = QUInt(num_bits, "b", qc)
    c = QUInt(2 * num_bits, "c", qc)

    x = x_in
    y = y_in
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

#workbench is little endian -> LE for some q# functions
#q# is big endian

@pytest.mark.parametrize("num_bits", [2, 5, 8, 10])
def test_sb_multiplier(num_bits: int):
    _check_multiplier(schoolbook_multiplication(), num_bits, num_trials=5)

#@pytest.mark.parametrize("num_bits", [2])
#def test_sb_multiplier(num_bits: int):
#    _check_multiplier_set(schoolbook_multiplication(), num_bits, 3, 3)
