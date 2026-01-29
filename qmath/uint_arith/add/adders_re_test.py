import pytest

from qmath.uint_arith.add import CDKMAdder, TTKAdder
from qmath.utils.re_utils import re_numeric_int_binary_op, re_symbolic_int_binary_op, verify_re


@pytest.mark.re
@pytest.mark.parametrize("controlled", [False, True])
def test_adder_ttk_re(controlled: bool):
    adder = TTKAdder()
    re_symbolic = re_symbolic_int_binary_op(adder, controlled=controlled)
    re_numeric = lambda assgn: re_numeric_int_binary_op(adder, assgn, controlled=controlled)
    for n in [2, 8, 20, 40]:
        verify_re(re_symbolic, re_numeric, {"n": n})


@pytest.mark.re
@pytest.mark.parametrize("controlled", [False, True])
def test_adder_cdkm_re(controlled: bool):
    adder = CDKMAdder()
    re_symbolic = re_symbolic_int_binary_op(adder, controlled=controlled)
    re_numeric = lambda assgn: re_numeric_int_binary_op(adder, assgn, controlled=controlled)
    for n in [5, 10, 20, 30, 40]:
        verify_re(re_symbolic, re_numeric, {"n": n})
