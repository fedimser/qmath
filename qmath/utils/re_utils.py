from psiqworkbench import QPU, SymbolicQPU, QUInt, SymbolicQubits, resource_estimator, Qubrick

from psiqworkbench.symbolics import Parameter
from psiqworkbench import SymbolicQPU, SymbolicQubits, Qubits
from psiqworkbench.utils.unstable_api_utils import ignore_unstable_warnings
from psiqworkbench.resource_estimation.qre._resource_dict import ResourceDict
from typing import Callable

import numpy as np

ignore_unstable_warnings()


def re_numeric_int_binary_op(op: Qubrick, assgn: dict[str, int], controlled=False) -> ResourceDict:
    """Numeric resource estimation for binary op on QUInts."""
    n = assgn["n"]
    qc = QPU(filters=[">>witness>>"])
    qc.reset(3 * n)
    qs_x = QUInt(n, "x", qc)
    qs_y = QUInt(n, "y", qc)
    ctrl = None
    if controlled:
        ctrl = Qubits(1, "ctrl", qc)
    op.compute(qs_x, qs_y, ctrl=ctrl)

    re = resource_estimator(qc)
    return re.resources()


def re_symbolic_int_binary_op(op: Qubrick, controlled=False) -> ResourceDict:
    """Symbolic resource estimation for binary op on QUInts."""
    n = Parameter("n", "Register size")
    qc = SymbolicQPU()
    qs_x = SymbolicQubits(n, "x", qc)
    qs_y = SymbolicQubits(n, "y", qc)
    ctrl = None
    if controlled:
        ctrl = SymbolicQubits(1, "ctrl", qc)
    op.compute(qs_x, qs_y, ctrl=ctrl)

    re = resource_estimator(qc)
    return re.resources()


METRICS = [
    "gidney_lelbows",
    "gidney_relbows",
    "measurements",
    "rotations",
    "t_gates",
    "toffs",
    "qubit_highwater",
    "active_volume",
]


def verify_re(
    re_symbolic: ResourceDict,
    re_numeric: Callable[[dict[str, int]], ResourceDict],
    assgn: dict[str, int],
    *,
    av_tol: float = 0.0,
    no_fail=False,
):
    """
    Test helper to verify that numeric and ysmbolic resource estimates match.

    :param re_symbolic: Symbolic resource estimate.
    :param re_numeric: Function to compute numeric RE for given assignment.
    :param assgn: Assignment (maps param name to value).
    :param av_tol: Relative tolerance for active volume.
    :param no_fail: If true, will print errors but not fail the test.
    """
    re1 = re_numeric(assgn)
    re2 = re_symbolic.evaluate(assgn)
    for metric in METRICS:
        tol = av_tol if metric == "active_volume" else 0.0
        if not np.isclose(re1[metric], re2[metric], rtol=tol):
            error = " ".join(
                [
                    f"Mismatch: {metric}.",
                    f"Numeric: {re1[metric]}.",
                    f"Symbolic: {re_symbolic[metric]} = {re2[metric]}.",
                    f"Diff: {re1[metric]-re2[metric]}",
                    f"Parameters: {assgn}.",
                ]
            )
            if no_fail:
                print(error)
            else:
                raise AssertionError(error)
