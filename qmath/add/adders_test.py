import random

import psiqworkbench.qubricks as qbk
import pytest
from psiqworkbench import QPU, QUInt
from psiqworkbench.interfaces import Adder

from qmath.add import CdkmAdder


# Tests in-place adder when both registers are of the same size and result is
# computed modulo n.
def _check_adder_modular(adder: Adder, num_bits, num_trials=10):
    qc = QPU(filters=[">>64bit>>", ">>bit-sim>>"])
    qc.reset(3 * num_bits - 1)

    qs_x = QUInt(num_bits, "a", qc)
    qs_y = QUInt(num_bits, "b", qc)
    for _ in range(num_trials):
        x = random.randint(0, 2**num_bits - 1)
        y = random.randint(0, 2**num_bits - 1)
        qs_x.write(x)
        qs_y.write(y)
        adder.compute(qs_x, qs_y)
        assert qs_x.read() == (x + y) % (2**num_bits)


# Tests in-place adder when there is extra carry qubit in the result register.
def _check_adder_with_carry_out(adder: Adder, num_bits, num_trials=10):
    qc = QPU(filters=[">>64bit>>", ">>bit-sim>>"])
    qc.reset(3 * num_bits + 1)

    qs_x = QUInt(num_bits + 1, "a", qc)
    qs_y = QUInt(num_bits, "b", qc)
    for _ in range(num_trials):
        x = random.randint(0, 2**num_bits - 1)
        y = random.randint(0, 2**num_bits - 1)
        print(x, y)
        qs_x.write(x)
        qs_y.write(y)
        adder.compute(qs_x, qs_y)
        assert qs_x.read() == x + y


def test_adder_naive():
    _check_adder_modular(qbk.NaiveAdd(), 10)
    _check_adder_with_carry_out(qbk.NaiveAdd(), 10)


def test_adder_gidney():
    _check_adder_modular(qbk.GidneyAdd(), 10)
    _check_adder_with_carry_out(qbk.GidneyAdd(), 50)


@pytest.mark.parametrize("num_bits", [1, 2, 3, 5, 10])
def test_adder_cdkm_unoptimized(num_bits: int):
    _check_adder_modular(CdkmAdder(optimized=False), num_bits)
    _check_adder_with_carry_out(CdkmAdder(optimized=False), num_bits)


@pytest.mark.parametrize("num_bits", [1, 2, 3, 5, 10])
def test_adder_cdkm_optimized(num_bits: int):
    _check_adder_modular(CdkmAdder(optimized=True), num_bits)
    _check_adder_with_carry_out(CdkmAdder(optimized=True), num_bits)
