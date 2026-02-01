import random

import pytest
from psiqworkbench import QPU, QUInt, SymbolicQPU, SymbolicQubits, resource_estimator
from psiqworkbench.filter_presets import BIT_DEFAULT

from qmath.utils.perm import ApplyPermutation, RotateRight, rotate_left, rotate_right


def test_perm_to_cycles():
    op = ApplyPermutation([2, 4, 3, 1, 0, 5, 7, 6])
    assert op.n == 8
    assert op.cycles == [[0, 2, 3, 1, 4], [6, 7]]


def _apply_permutation(x, perm):
    n = len(perm)
    bits = [(x >> i) % 2 for i in range(n)]
    bits = [bits[perm[i]] for i in range(n)]
    return sum(bits[i] * 2**i for i in range(n))


@pytest.mark.parametrize("n", [5, 10])
def test_apply_permutation(n: int):
    for _ in range(10):
        perm = list(range(n))
        random.shuffle(perm)
        x = random.randint(0, 2**n - 1)
        qpu = QPU(filters=BIT_DEFAULT)
        qpu.reset(n)
        qs_x = QUInt(n, name="x", qpu=qpu)
        qs_x.write(x)

        op = ApplyPermutation(perm)
        op.compute(qs_x)

        assert qs_x.read() == _apply_permutation(x, perm)


def _rotate_right(x, n, shift):
    assert 0 < shift < n
    bits = [(x >> i) % 2 for i in range(n)]
    bits = bits[-shift:] + bits[0:-shift]
    return sum(bits[i] * 2**i for i in range(n))


@pytest.mark.parametrize("n", [5, 10])
def test_rotate(n: int):
    for _ in range(10):
        shift = random.randint(1, n - 1)
        x = random.randint(0, 2**n - 1)
        qpu = QPU(filters=BIT_DEFAULT)
        qpu.reset(n)
        qs_x = QUInt(n, name="x", qpu=qpu)
        qs_x.write(x)

        op = RotateRight(shift)
        op.compute(qs_x)

        assert qs_x.read() == _rotate_right(x, n, shift)


def test_rotate_for_mul():
    n = 8
    qpu = QPU(filters=BIT_DEFAULT)
    qpu.reset(n)
    qs_x = QUInt(n, name="x", qpu=qpu)
    qs_x.write(3)
    op = RotateRight(2)
    op.compute(qs_x)
    assert qs_x.read() == 12


@pytest.mark.smoke
def test_rotate_left():
    n = 8
    qpu = QPU(filters=BIT_DEFAULT)
    qpu.reset(n)
    qs_x = QUInt(n, name="x", qpu=qpu)
    qs_x.write(6)
    rotate_left(qs_x)
    assert qs_x.read() == 3


@pytest.mark.smoke
def test_rotate_right():
    n = 8
    qpu = QPU(filters=BIT_DEFAULT)
    qpu.reset(n)
    qs_x = QUInt(n, name="x", qpu=qpu)
    qs_x.write(6)
    rotate_right(qs_x)
    assert qs_x.read() == 12
