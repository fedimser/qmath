from qmath.utils.re_utils import re_numeric_int_binary_op, re_symbolic_int_binary_op, verify_re
from qmath.add import TTKAdder, CDKMAdder


def test_adder_ttk_re():
    adder = TTKAdder()
    re_symbolic = re_symbolic_int_binary_op(adder)
    re_numeric = lambda assgn: re_numeric_int_binary_op(adder, assgn)
    for n in [2, 8, 20, 40]:
        verify_re(re_symbolic, re_numeric, {"n": n})


def test_adder_cdkm_re():
    adder = CDKMAdder()
    re_symbolic = re_symbolic_int_binary_op(adder)
    re_numeric = lambda assgn: re_numeric_int_binary_op(adder, assgn)
    for n in [5, 10, 20, 30, 40]:
        verify_re(re_symbolic, re_numeric, {"n": n})
