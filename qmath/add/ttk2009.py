from typing import Optional

from psiqworkbench import Qubits, QUInt
from psiqworkbench.interfaces import Adder
from psiqworkbench.interoperability import implements
from psiqworkbench.qubricks import Qubrick
from psiqworkbench.symbolics.qubrick_costs import QubrickCosts

from ..utils.padding import padded


class ApplyOuterTTKAdder(Qubrick):
    def _compute(self, rhs: Qubits, lhs: Qubits, ctrl: Optional[Qubits] = None):
        assert len(rhs) <= len(lhs), "Input register lhs must be at least as long as rhs."
        for i in range(1, len(rhs)):
            lhs[i].x(rhs[i] | ctrl)
        for i in range(len(rhs) - 2, 0, -1):
            rhs[i + 1].x(rhs[i] | ctrl)


class ApplyInnerTTKAdderNoCarry(Qubrick):
    def _compute(self, rhs: Qubits, lhs: Qubits, ctrl: Optional[Qubits] = None):
        assert len(rhs) == len(lhs)
        for idx in range(len(rhs) - 1):
            rhs[idx + 1].x(rhs[idx] | lhs[idx])
        for idx in range(len(rhs) - 1, 0, -1):
            lhs[idx].x(rhs[idx] | ctrl)
            rhs[idx].x(rhs[idx - 1] | lhs[idx - 1])


class ApplyInnerTTKAdderWithCarry(Qubrick):
    def _compute(self, rhs: Qubits, lhs: Qubits, ctrl: Optional[Qubits] = None):
        n = len(rhs)
        assert n + 1 == len(lhs), "lhs must be one qubit longer then rhs."
        assert n > 0, "rhs should not be empty."
        for idx in range(n - 1):
            rhs[idx + 1].x(rhs[idx] | lhs[idx])
        lhs[n].x(rhs[n - 1] | lhs[n - 1] | ctrl)
        for idx in range(n - 1, 0, -1):
            lhs[idx].x(rhs[idx] | ctrl)
            rhs[idx].x(rhs[idx - 1] | lhs[idx - 1])


@implements(Adder[QUInt, QUInt])
class TTKAdder(Qubrick):
    """Computes lhs += rhs modulo 2^n using ripple-carry addition algorithm.

    Requires len(rhs) <= len(lhs) = n.

    If len(rhs) <= len(lhs)-2, rhs is padded with 0-initialized qubits.

    Implementation of the adder presented in paper:
        "Quantum Addition Circuits and Unbounded Fan-Out",
        Yasuhiro Takahashi, Seiichiro Tani, Noboru Kunihiro, 2009.
        https://arxiv.org/abs/0910.2530
    """

    def _compute(self, lhs: QUInt, rhs: QUInt, ctrl: Optional[Qubits] = None):
        rhs_len = rhs.num_qubits
        lhs_len = lhs.num_qubits
        assert lhs_len >= rhs_len, "Register `rhs` cannot be longer than register `lhs`."
        assert rhs_len >= 1, "Registers `rhs` and `lhs` must contain at least one qubit."

        if rhs_len == lhs_len:
            if rhs_len > 1:
                with ApplyOuterTTKAdder().computed(rhs, lhs, ctrl=ctrl):
                    ApplyInnerTTKAdderNoCarry().compute(rhs, lhs, ctrl=ctrl)
            lhs[0].x(rhs[0] | ctrl)
        elif rhs_len + 1 == lhs_len:
            if rhs_len > 1:
                lhs[lhs_len - 1].x(rhs[rhs_len - 1] | ctrl)
                with ApplyOuterTTKAdder().computed(rhs, lhs, ctrl=ctrl):
                    ApplyInnerTTKAdderWithCarry().compute(rhs, lhs, ctrl=ctrl)
            else:
                lhs[1].x(rhs[0] | lhs[0] | ctrl)
            lhs[0].x(rhs[0] | ctrl)
        else:
            assert rhs_len + 2 <= lhs_len
            # Pad rhs so that its length is one qubit shorter than lhs.
            with padded(self, (rhs,), (len(lhs) - 1,)) as (rhs,):
                assert len(rhs) == len(lhs) - 1
                self._compute(lhs, rhs)

    def _estimate(self, lhs: QUInt, rhs: QUInt, ctrl: Optional[Qubits] = None):
        assert ctrl is None, "RE not implemented for controlled version."
        assert lhs.num_qubits == rhs.num_qubits, "RE implemented only for inputs of equal size."
        n = lhs.num_qubits
        # Note: this RE is correct only for n>=2.

        cost = QubrickCosts(
            toffs=2 * n - 2,
            active_volume=114 * n - 118,
        )
        self.get_qc().add_cost_event(cost)
