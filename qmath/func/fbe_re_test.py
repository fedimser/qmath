from qmath.utils.re_utils import re_numeric_fixed_point, FILTERS_FOR_NUMERIC_RE
from psiqworkbench.symbolics import Parameter
from psiqworkbench.resource_estimation.qre._resource_dict import ResourceDict
from psiqworkbench import QPU, QUInt, SymbolicQPU, SymbolicQubits, resource_estimator, QFixed
from qmath.func.fbe import CosFbe
from qmath.utils.symbolic import SymbolicQFixed
import numpy as np
import os
from qmath.utils.re_utils import verify_re


RUN_SLOW_TESTS = os.getenv("RUN_SLOW_TESTS") == "1"


def re_symbolic_CosFbe() -> ResourceDict:
    n = Parameter("n", "Input radix")
    m = Parameter("m", "Result radix")
    op = CosFbe(result_radix=m)

    qpu = SymbolicQPU()
    qs_x = SymbolicQFixed(num_qubits=n + 2, name="x", qpu=qpu, radix=n)
    op.compute(qs_x)
    return resource_estimator(qpu).resources()


def re_numeric_CosFbe(assgn: dict[str, int]) -> ResourceDict:
    """Numeric resource estimation for multiplier."""
    n, m = assgn["n"], assgn["m"]
    op = CosFbe(result_radix=m)

    qpu = QPU(filters=FILTERS_FOR_NUMERIC_RE)
    qpu.reset(n * m + 3 * n + m + 12)
    qs_x = QFixed(n + 2, name="x", qpu=qpu, radix=n)
    op.compute(qs_x)
    return resource_estimator(qpu).resources()


def test_re_CosFbe():
    re_symbolic = re_symbolic_CosFbe()
    re_numeric = re_numeric_CosFbe
    test_cases = [(2, 2), (3, 4), (5, 8)]
    if RUN_SLOW_TESTS:
        test_cases += [(10, 10), (15, 10), (10, 16)]
    for n, m in test_cases:
        verify_re(re_symbolic, re_numeric, {"n": n, "m": m})
