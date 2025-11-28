import random

import psiqworkbench.qubricks as qbk
import pytest
from psiqworkbench import QPU, QUInt
from psiqworkbench.interfaces import Adder

from qmath.add import CDKMAdder, TTKAdder


# Tests in-place adder:
#   * Initializes two registers: x of size n1 and y of size n2.
#   * Fills them with random numbers.
#   * Calls adder to compute x += y.
#   * Check that result is computed correctly modulo 2**n1.
def _check_adder(adder: Adder, num_bits: tuple[int, int], num_trials=5):
    n1, n2 = num_bits
    assert n1 >= n2
    qc = QPU(filters=[">>64bit>>", ">>bit-sim>>"])
    qc.reset(2 * n1 + n2)

    qs_x = QUInt(n1, "a", qc)
    qs_y = QUInt(n2, "b", qc)
    for _ in range(num_trials):
        x = random.randint(0, 2**n1 - 1)
        y = random.randint(0, 2**n2 - 1)
        qs_x.write(x)
        qs_y.write(y)
        adder.compute(qs_x, qs_y)
        assert qs_x.read() == (x + y) % (2**n1)


def test_adder_naive():
    _check_adder(qbk.NaiveAdd(), (10, 10))
    _check_adder(qbk.NaiveAdd(), (10, 5))


def test_adder_gidney():
    _check_adder(qbk.GidneyAdd(), (10, 10))
    _check_adder(qbk.GidneyAdd(), (10, 5))


@pytest.mark.parametrize("num_bits", [(1, 1), (2, 1), (2, 2), (8, 8), (10, 10), (10, 9), (20, 20)])
def test_adder_cdkm_unoptimized(num_bits: tuple[int, int]):
    _check_adder(CDKMAdder(optimized=False), num_bits)


@pytest.mark.parametrize("num_bits", [(1, 1), (2, 1), (2, 2), (8, 8), (10, 10), (10, 9), (20, 20)])
def test_adder_cdkm_optimized(num_bits: int):
    _check_adder(CDKMAdder(optimized=True), num_bits)


@pytest.mark.parametrize("num_bits", [(1, 1), (2, 1), (2, 2), (8, 8), (10, 10), (10, 9), (10, 5), (20, 20)])
def test_adder_ttk(num_bits: int):
    _check_adder(TTKAdder(), num_bits)
