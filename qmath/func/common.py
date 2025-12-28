"""Common functions on QFixed numbers, used as building blocks in other routines.

Some of these are wrappers around routines from psiqworkbench.qubricks, this is
done so we can define symbolic resource estimates for them.
"""

import psiqworkbench.qubricks as qbk
from psiqworkbench import QFixed, Qubrick, QInt, QUInt
from psiqworkbench.symbolics.qubrick_costs import QubrickCosts

from ..utils.symbolic import SymbolicQFixed


class Negate(Qubrick):
    """Computes x:=-x."""

    def _compute(self, x: QFixed):
        x_as_int = QInt(x)
        x_as_int.x()
        qbk.GidneyAdd().compute(x_as_int, 1)

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
        # Using loop instead of x.x(sign) to get exact symbolic RE.
        # TODO: understand why x.x(sign) has non-linear numeric RE.
        for i in range(x.num_qubits):
            x[i].x(sign)
        qbk.GidneyAdd().compute(QUInt(x), 1, ctrl=sign)

    def _estimate(self, x: SymbolicQFixed):
        n = x.num_qubits
        cost = QubrickCosts(
            gidney_lelbows=n - 2,
            gidney_relbows=n - 2,
            toffs=n - 1,
            local_ancillae=n - 1,
            active_volume=108 * n - 154,
        )
        self.get_qc().add_cost_event(cost)


class Add(Qubrick):
    """Computes lhs+= rhs."""

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


class Subtract(Qubrick):
    """Computes lhs-= rhs. Negates rhs in the process."""

    def _compute(self, lhs: QFixed, rhs: QFixed):
        Negate().compute(rhs)
        Add().compute(lhs, rhs)


class MultiplyAdd(Qubrick):
    """Computes dst += (lhs * rhs)."""

    def _compute(self, dst: QFixed, lhs: QFixed, rhs: QFixed):
        qbk.GidneyMultiplyAdd().compute(dst, lhs, rhs)

    def _estimate(self, dst: SymbolicQFixed, lhs: SymbolicQFixed, rhs: SymbolicQFixed):
        n = dst.num_qubits
        assert lhs.num_qubits == n
        assert rhs.num_qubits == n
        # TODO: implement.
        cost = QubrickCosts(
            local_ancillae=0,
            active_volume=0,
            gidney_lelbows=0,
        )
        self.get_qc().add_cost_event(cost)
