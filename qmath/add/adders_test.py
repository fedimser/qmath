import random

import psiqworkbench.qubricks as qbk
from psiqworkbench import QPU, QUInt
from psiqworkbench.interfaces import Adder
from qmath.add import CdkmAdder


def _check_adder(adder: Adder, num_bits):
    qc = QPU(filters=[">>64bit>>", ">>bit-sim>>"])
    qc.reset(3 * num_bits - 1)

    a = QUInt(num_bits, "a", qc)
    b = QUInt(num_bits, "b", qc)
    for _ in range(1):
        x = random.randint(0, 2**num_bits - 1)
        y = random.randint(0, 2**num_bits - 1)
        expected = (x + y) % (2**num_bits)
        a.write(x)
        b.write(y)
        adder.compute(a, b)
        assert a.read() == expected


def test_adder_naive():
    _check_adder(qbk.NaiveAdd(), 10)


def test_adder_gidney():
    _check_adder(qbk.GidneyAdd(), 10)


def test_adder_cdkm():
    _check_adder(CdkmAdder(), 10)
