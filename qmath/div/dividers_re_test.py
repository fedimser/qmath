import pytest
from psiqworkbench import QPU, QUInt, SymbolicQPU, SymbolicQubits, resource_estimator
from psiqworkbench.resource_estimation.qre._resource_dict import ResourceDict
from psiqworkbench.symbolics import Parameter

from qmath.div import TMVHDivider
from qmath.utils.re_utils import verify_re, FILTERS_FOR_NUMERIC_RE


def re_symbolic_divider(op: TMVHDivider) -> ResourceDict:
    """Symbolic resource estimation for multiplier."""
    na = Parameter("na", "Dividend size")
    nb = Parameter("nb", "Divisor size")

    qc = SymbolicQPU()
    qs_a = SymbolicQubits(na, "a", qc)
    qs_b = SymbolicQubits(nb, "b", qc)
    qs_c = SymbolicQubits(na, "c", qc)
    op.compute(qs_a, qs_b, qs_c)

    re = resource_estimator(qc)
    return re.resources()


def re_numeric_divider(op: TMVHDivider, assgn: dict[str, int]) -> ResourceDict:
    """Numeric resource estimation for multiplier."""
    na, nb = assgn["na"], assgn["nb"]
    qc = QPU(filters=FILTERS_FOR_NUMERIC_RE)
    qc.reset(4 * na + 5)
    qs_a = QUInt(na, "a", qc)
    qs_b = QUInt(nb, "b", qc)
    qs_c = QUInt(na, "c", qc)
    op.compute(qs_a, qs_b, qs_c)

    re = resource_estimator(qc)
    return re.resources()


@pytest.mark.parametrize("restoring", [True, False])
def test_re_tmvh_divider(restoring: bool):
    op = TMVHDivider(restoring=restoring)
    re_symbolic = re_symbolic_divider(op)
    re_numeric = lambda assgn: re_numeric_divider(op, assgn)
    for na, nb in [(2, 2), (5, 3), (8, 7), (10, 10)]:
        verify_re(re_symbolic, re_numeric, {"na": na, "nb": nb})
