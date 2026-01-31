import random

import pytest
from psiqworkbench import QPU, QUInt, SymbolicQPU, SymbolicQubits, resource_estimator
from psiqworkbench.filter_presets import BIT_DEFAULT

from qmath.utils.perm import ApplyPermutation


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
