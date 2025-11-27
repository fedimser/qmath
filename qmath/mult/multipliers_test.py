import random

from psiqworkbench import QPU, QUInt
from qmath.mult import JhhaMultipler, MctMultipler, Multiplier


def _check_multiplier(multiplier: Multiplier, num_bits):
    qc = QPU(filters=[">>64bit>>", ">>bit-sim>>"])
    qc.reset(4 * num_bits + 1)

    a = QUInt(num_bits, "a", qc)
    b = QUInt(num_bits, "b", qc)
    c = QUInt(2 * num_bits, "c", qc)

    for _ in range(10):
        x = random.randint(0, 2**num_bits - 1)
        y = random.randint(0, 2**num_bits - 1)
        a.write(x)
        b.write(y)
        c.write(0)
        multiplier.compute(a, b, c)
        assert c.read() == x * y


def test_mct_multiplier():
    _check_multiplier(MctMultipler(), 10)


def test_jhha_multiplier():
    _check_multiplier(JhhaMultipler(), 10)
