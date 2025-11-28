import random

import numpy as np
import psiqworkbench.qubricks as qbk
import pytest
from psiqworkbench import QPU, Qubits, QUInt
from psiqworkbench.interfaces import Adder

from qmath.add import CDKMAdder, TTKAdder


# Tests in-place adder:
#   * Initializes two registers: x of size n1 and y of size n2.
#   * Fills them with random numbers.
#   * Calls adder to compute x += y.
#   * Check that result is computed correctly modulo 2**n1.
def _check_adder(adder: Adder, n1: int, n2: int, num_trials=5):
    assert n1 >= n2
    qc = QPU(filters=[">>64bit>>", ">>bit-sim>>"])
    qc.reset(2 * n1 + n2)

    qs_x = QUInt(n1, "x", qc)
    qs_y = QUInt(n2, "y", qc)
    for _ in range(num_trials):
        x = random.randint(0, 2**n1 - 1)
        y = random.randint(0, 2**n2 - 1)
        qs_x.write(x)
        qs_y.write(y)
        adder.compute(qs_x, qs_y)
        assert qs_x.read() == (x + y) % (2**n1)


def _check_controlled_adder(adder: Adder, n1: int, n2: int, num_trials=5):
    assert n1 >= n2
    qc = QPU()
    qc.reset(2 * n1 + n2)

    qs_x = QUInt(n1, "x", qc)
    qs_y = QUInt(n2, "y", qc)
    qs_ctrl = Qubits(1, "ctrl", qc)
    for _ in range(num_trials):
        x = random.randint(0, 2**n1 - 1)
        y = random.randint(0, 2**n2 - 1)
        qs_x.write(x)
        qs_y.write(y)
        qs_ctrl.write(0)
        qs_ctrl.had()
        adder.compute(qs_x, qs_y, ctrl=qs_ctrl)

        # qs_x is expected to be in equal superposition of x and (x+y)%(2**n1).
        state = qc.pull_state(with_qreg_labels=True)
        assert state["qregs"] == ("x", "y", "ctrl")
        amps = state["amps"]
        assert amps.keys() == {(x, y, 0), ((x + y) % (2**n1), y, 1)}
        assert np.allclose(np.array(list(amps.values())), 2**-0.5)


def test_adder_naive():
    _check_adder(qbk.NaiveAdd(), 10, 10)
    _check_adder(qbk.NaiveAdd(), 10, 5)


def test_adder_naive_controlled():
    _check_controlled_adder(qbk.NaiveAdd(), 3, 3)


def test_adder_gidney():
    _check_adder(qbk.GidneyAdd(), 10, 10)
    _check_adder(qbk.GidneyAdd(), 10, 5)


def test_adder_gidney_controlled():
    _check_controlled_adder(qbk.GidneyAdd(), 3, 3)


@pytest.mark.parametrize("num_bits", [(1, 1), (2, 1), (2, 2), (8, 8), (10, 10), (10, 9), (10, 5), (20, 20)])
def test_adder_cdkm_unoptimized(num_bits: tuple[int, int]):
    n1, n2 = num_bits
    _check_adder(CDKMAdder(optimized=False), n1, n2)


@pytest.mark.parametrize("num_bits", [(1, 1), (2, 1), (2, 2), (8, 8), (10, 10), (10, 9), (10, 5), (20, 20)])
def test_adder_cdkm_optimized(num_bits: tuple[int, int]):
    n1, n2 = num_bits
    _check_adder(CDKMAdder(optimized=True), n1, n2)


def test_adder_cdkm_controlled():
    _check_controlled_adder(CDKMAdder(optimized=False), 5, 4)
    _check_controlled_adder(CDKMAdder(optimized=False), 5, 5)
    _check_controlled_adder(CDKMAdder(optimized=True), 5, 4)
    _check_controlled_adder(CDKMAdder(optimized=True), 5, 5)


@pytest.mark.parametrize("num_bits", [(1, 1), (2, 1), (2, 2), (8, 8), (10, 10), (10, 9), (10, 5), (20, 20)])
def test_adder_ttk(num_bits: tuple[int, int]):
    n1, n2 = num_bits
    _check_adder(TTKAdder(), n1, n2)


def test_adder_ttk_controlled():
    _check_controlled_adder(TTKAdder(), 5, 5)
    _check_controlled_adder(TTKAdder(), 5, 4, num_trials=10)
