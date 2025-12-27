from psiqworkbench import QPU, QUInt, SymbolicQPU, SymbolicQubits, resource_estimator
from psiqworkbench.resource_estimation.qre._resource_dict import ResourceDict
from psiqworkbench.symbolics import Parameter

from qmath.mult import JHHAMultipler, MCTMultipler, Multiplier
from qmath.utils.re_utils import verify_re


def re_symbolic_multiplier(op: Multiplier) -> ResourceDict:
    """Symbolic resource estimation for multiplier."""
    n = Parameter("n", "Register size")
    qc = SymbolicQPU()
    qs_x = SymbolicQubits(n, "x", qc)
    qs_y = SymbolicQubits(n, "y", qc)
    qs_z = SymbolicQubits(2 * n, "z", qc)
    op.compute(qs_x, qs_y, qs_z)

    re = resource_estimator(qc)
    return re.resources()


def re_numeric_multiplier(op: Multiplier, assgn: dict[str, int]) -> ResourceDict:
    """Numeric resource estimation for multiplier."""
    n = assgn["n"]
    qc = QPU(filters=[">>witness>>"])
    qc.reset(4 * n + 1)
    qs_x = QUInt(n, "x", qc)
    qs_y = QUInt(n, "y", qc)
    qs_z = QUInt(2 * n, "z", qc)
    op.compute(qs_x, qs_y, qs_z)

    re = resource_estimator(qc)
    return re.resources()


def test_re_jhha():
    op = JHHAMultipler()
    re_symbolic = re_symbolic_multiplier(op)
    re_numeric = lambda assgn: re_numeric_multiplier(op, assgn)
    for n in [1, 5, 10, 20]:
        verify_re(re_symbolic, re_numeric, {"n": n})
