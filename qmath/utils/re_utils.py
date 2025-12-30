from typing import Callable

import numpy as np
from psiqworkbench import QPU, QFixed, Qubits, Qubrick, QUInt, SymbolicQPU, SymbolicQubits, resource_estimator
from psiqworkbench.resource_estimation.qre._resource_dict import ResourceDict
from psiqworkbench.symbolics import Parameter
from psiqworkbench.utils.unstable_api_utils import ignore_unstable_warnings
from psiqworkbench.utils import bit_utils

from ..utils.symbolic import SymbolicQFixed

ignore_unstable_warnings()

FILTERS_FOR_NUMERIC_RE = [">>clean-ladder-filter>>", ">>single-control-filter>>", ">>witness>>"]


def re_numeric_int_binary_op(op: Qubrick, assgn: dict[str, int], controlled=False) -> ResourceDict:
    """Numeric resource estimation for binary op on QUInts."""
    n = assgn["n"]
    qc = QPU(filters=FILTERS_FOR_NUMERIC_RE)
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


# TODO: use psiqworkbench.test_helpers.compare_costs.
def verify_re(
    re_symbolic: ResourceDict,
    re_numeric: Callable[[dict[str, int]], ResourceDict],
    assgn: dict[str, int],
    *,
    av_rtol: float = 0.0,
    av_atol: float = 0.0,
    elbows_rtol: float = 0.0,
    no_fail=False,
):
    """
    Test helper to verify that numeric and ysmbolic resource estimates match.

    :param re_symbolic: Symbolic resource estimate.
    :param re_numeric: Function to compute numeric RE for given assignment.
    :param assgn: Assignment (maps param name to value).
    :param av_rtol: Relative tolerance for active volume.
    :param av_atol: Absolute tolerance for active volume.
    :param no_fail: If true, will print errors but not fail the test.
    """
    re1 = re_numeric(assgn)
    re2 = re_symbolic.evaluate(assgn)
    for metric in METRICS:
        rtol = 0.0
        if metric == "active_volume":
            rtol = av_rtol
        elif metric.endswith("elbows"):
            rtol = elbows_rtol
        atol = av_atol if metric == "active_volume" else 0.0
        if not np.isclose(re1[metric], re2[metric], rtol=rtol, atol=atol):
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


def re_symbolic_fixed_point(op: Qubrick, n_inputs: int = 1) -> ResourceDict:
    """Symbolic resource estimation for fixed-point operation."""
    n = Parameter("n", "Register size")
    radix = Parameter("radix", "Radix size")

    qpu = SymbolicQPU()
    inputs = [SymbolicQFixed(num_qubits=n, name=f"input_{i}", qpu=qpu, radix=radix) for i in range(n_inputs)]
    op.compute(*inputs)

    re = resource_estimator(qpu)
    return re.resources()


def re_numeric_fixed_point(
    op: Qubrick,
    assgn: dict[str, int],
    n_inputs: int = 1,
    qubits_factor: int = 10,
) -> ResourceDict:
    """Numeric resource estimation for fixed-point operation.

    :param op: Operation to resource-estimate.
    :param assgn: Dictionary with 2 keys ("n", "radix") - register size and radix.
    :param n_inputs: Number of input registers.
    :param qubits_factor: Upper-bound estimate for ratio of total qubits needed to register size.
        Used to compute number of qubits in simulator.
    """
    n, radix = assgn["n"], assgn["radix"]
    qpu = QPU(filters=FILTERS_FOR_NUMERIC_RE)
    qpu.reset(qubits_factor * n)
    inputs = [QFixed(n, name=f"input_{i}", radix=radix, qpu=qpu) for i in range(n_inputs)]
    op.compute(*inputs)

    re = resource_estimator(qpu)
    return re.resources()


def fraction_length(x: float, max_length: int = 10) -> int | None:
    """Returns length of fractional part of x in binary representation.

    If x is integer, return -num_trailing_zeros(x).
    If fractional part is not finite or longer than `max_length`, returns None.
    """
    x = float(x)
    if int(x) == x:
        return -bit_utils.num_trailing_zeros(x)
    for i in range(1, max_length + 1):
        x *= 2
        if x.is_integer():
            return i
    return None
