import random

import pytest
from psiqworkbench import QPU, QUInt
from psiqworkbench.filter_presets import BIT_DEFAULT

from ..add import CDKMAdder, TTKAdder
from ..div import TMVHDivider


def _check_divider(divider: TMVHDivider, num_bits: tuple[int, int], num_trials=2):
    na, nb = num_bits
    assert 0 < nb <= na
    qc = QPU(filters=BIT_DEFAULT)
    qc.reset(4 * na + 5)

    qs_a = QUInt(na, "a", qc)
    qs_b = QUInt(nb, "b", qc)
    qs_c = QUInt(na, "c", qc)

    for _ in range(num_trials):
        a = random.randint(0, 2**na - 1)
        b = random.randint(1, 2**nb - 1)
        qs_a.write(a)
        qs_b.write(b)
        qs_c.write(0)
        divider.compute(qs_a, qs_b, qs_c)
        assert qs_a.read() == a % b
        assert qs_b.read() == b
        assert qs_c.read() == a // b


@pytest.mark.parametrize("num_bits", [(1, 1), (2, 1), (2, 2), (10, 10), (10, 9), (10, 5)])
def test_tmvh_divider_restoring(num_bits: tuple[int, int]):
    _check_divider(TMVHDivider(restoring=True), num_bits)


@pytest.mark.parametrize("num_bits", [(1, 1), (2, 1), (2, 2), (10, 10), (10, 9), (10, 5)])
def test_tmvh_divider_non_restoring(num_bits: tuple[int, int]):
    _check_divider(TMVHDivider(restoring=False), num_bits)


def test_tmvh_different_adders():
    _check_divider(TMVHDivider(restoring=False, adder=TTKAdder()), (10, 10))
    _check_divider(TMVHDivider(restoring=True, adder=TTKAdder()), (10, 10))
    _check_divider(TMVHDivider(restoring=False, adder=CDKMAdder()), (10, 10))
    _check_divider(TMVHDivider(restoring=True, adder=CDKMAdder()), (10, 10))
