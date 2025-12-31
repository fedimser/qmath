"""Common functions on QFixed numbers, used as building blocks in other routines.

Some of these are wrappers around routines from psiqworkbench.qubricks, this is
done so we can define symbolic resource estimates for them.
"""

import psiqworkbench.qubricks as qbk
from psiqworkbench import QFixed, Qubrick, QInt, QUInt, Qubits
from psiqworkbench.symbolics.qubrick_costs import QubrickCosts
from psiqworkbench.symbolics import Min

from ..utils.symbolic import SymbolicQFixed
from ..utils.re_utils import fraction_length


class Negate(Qubrick):
    """Computes x:=-x."""

    def _compute(self, x: QFixed, ctrl: Qubits | None = None):
        x_as_int = QInt(x)
        x_as_int.x(ctrl)
        qbk.GidneyAdd().compute(x_as_int, 1, ctrl=ctrl)

    def _estimate(self, x: SymbolicQFixed):
        n = x.num_qubits
        cost = QubrickCosts(
            gidney_lelbows=n - 2,
            gidney_relbows=n - 2,
            local_ancillae=n - 2,
            active_volume=61 * n - 118,
        )
        self.get_qc().add_cost_event(cost)


class AbsInPlace(Qubrick):
    """Computes x := abs(x)."""

    def _compute(self, x: QFixed):
        sign = self.alloc_temp_qreg(1, "sign")
        sign.lelbow(x[-1])
        x.x(sign)
        qbk.GidneyAdd().compute(QUInt(x), 1, ctrl=sign)

    def _estimate(self, x: SymbolicQFixed):
        n = x.num_qubits
        cost = QubrickCosts(
            gidney_lelbows=n - 2,
            gidney_relbows=n - 2,
            toffs=n - 1,
            local_ancillae=n - 1,
            active_volume=105.5 * n - 150,
        )
        self.get_qc().add_cost_event(cost)


class Add(Qubrick):
    """Computes lhs += rhs."""

    def _compute(self, lhs: QFixed, rhs: QFixed):
        qbk.GidneyAdd().compute(lhs, rhs)

    def _estimate(self, lhs: SymbolicQFixed, rhs: SymbolicQFixed):
        # qbk.GidneyAdd has _estimate, but active volume there differs from
        # what we observe from numeric RE. So we have to re-define _estimate.
        n = lhs.num_qubits
        cost = QubrickCosts(
            gidney_lelbows=n - 1,
            gidney_relbows=n - 1,
            local_ancillae=n - 1,
            active_volume=72 * n - 83,
        )
        self.get_qc().add_cost_event(cost)


class AddConst(Qubrick):
    """Computes lhs += rhs (a is aclassical number)."""

    def __init__(self, rhs: float, **kwargs):
        super().__init__(**kwargs)
        self.rhs = rhs
        if abs(self.rhs) < 1e-10:
            self.rhs = 0.0

    def _compute(self, lhs: QFixed):
        assert abs(self.rhs) <= 2 ** (lhs.num_qubits - lhs.radix - 1), f"Constant {self.rhs} is too large."
        qbk.GidneyAdd().compute(lhs, self.rhs)

    def _estimate(self, lhs: SymbolicQFixed):
        # This estimate might be off (overestimate) by O(1) in case when lhs
        # is not "round" number, but when rounded to fixed precision, few of
        # least significant bits become zeroes.
        # This estimate assumes that rhs fits in given register.

        # Compute n - length of rhs except trailing zeros.
        n = lhs.num_qubits
        fl = fraction_length(self.rhs)
        if fl is not None:
            n = Min(n, lhs.num_qubits - lhs.radix + fl)

        cost = QubrickCosts(
            gidney_lelbows=n - 2,
            gidney_relbows=n - 2,
            local_ancillae=n - 2,
            active_volume=61 * n - 118,
        )
        self.get_qc().add_cost_event(cost)


class Subtract(Qubrick):
    """Computes lhs-= rhs. Negates rhs in the process."""

    def _compute(self, lhs: QFixed, rhs: QFixed):
        Negate().compute(rhs)
        Add().compute(lhs, rhs)


class MultiplyAdd(Qubrick):
    """Computes dst += lhs * rhs."""

    def _compute(self, dst: QFixed, lhs: QFixed, rhs: QFixed):
        qbk.GidneyMultiplyAdd().compute(dst, lhs, rhs)

    def _estimate(self, dst: SymbolicQFixed, lhs: SymbolicQFixed, rhs: SymbolicQFixed):
        n = dst.num_qubits
        assert lhs.num_qubits == n
        assert rhs.num_qubits == n
        r = lhs.radix + rhs.radix - dst.radix

        # This RE is correct when n>=4, 0<r<n.
        # It is within 0.1% of numerical RE for active volume and exact for other metrics.
        cost = QubrickCosts(
            gidney_lelbows=0.5 * ((n + r) ** 2 + 15 * n - r - 32),
            gidney_relbows=0.5 * ((n + r) ** 2 + 15 * n - r - 32),
            toffs=0.5 * ((n + r) ** 2 + 17 * n + r - 16),
            local_ancillae=n + 2 * r + 1,
            active_volume=-1170 + 821 * n - 23 * r + 59 * n**2 + 118 * n * r + 54 * r**2,
        )
        self.get_qc().add_cost_event(cost)


# TODO: implement.
class MultiplyConstAdd(Qubrick):
    """Computes dst += lhs * rhs (rhs is a classical number)."""

    def __init__(self, rhs: float, **kwargs):
        super().__init__(**kwargs)
        self.rhs = rhs

    def _compute(self, dst: QFixed, lhs: QFixed):
        pass

    def _estimate(self, dst: SymbolicQFixed, lhs: SymbolicQFixed):
        pass
