import psiqworkbench.qubricks as qbk
from psiqworkbench import QFixed, Qubits, QUFixed
from psiqworkbench.qubricks import Qubrick
from psiqworkbench.symbolics.qubrick_costs import QubrickCosts

from ..func.common import AbsInPlace, MultiplyAdd
from ..utils.gates import ParallelCnot
from ..utils.symbolic import SymbolicQFixed, alloc_temp_qreg_like


class Square(Qubrick):
    """Computes square of given QFixed register by making a copy and calling MultiplyAdd."""

    def _compute(self, x: QFixed, target: QFixed):
        x_copy_reg, x_copy = alloc_temp_qreg_like(self, x)
        with ParallelCnot().computed(x, x_copy):
            MultiplyAdd().compute(target, x, x_copy)
        x_copy_reg.release()


class _SquareIteration(Qubrick):
    def _compute(self, x: Qubits, anc: Qubits, i: int, j: int, skip: int):
        if skip == 0:
            anc[j].lelbow(x[i])
        for i2 in range(max(1, skip - 1), x.num_qubits - i):
            anc_pos = j + (i2 - skip + 1)
            if anc_pos >= anc.num_qubits:
                break
            assert 0 <= anc_pos < anc.num_qubits
            anc[anc_pos].lelbow(x[i] | x[i + i2])


class SquareOptimized(Qubrick):
    """Computes square of given QFixed register.

    Uses algorithm from Lemma 6 in https://arxiv.org/pdf/2105.12767.

    This algorithm uses 2x less resources but requires ~1 extra qubit to achieve
    the same precision as square via multiplication. This is because it doesn't
    add padding qubits so result.radix=x.radix*2, like the multiplication does.

    TODO: achieve the same precision as Square by padding with
    log2(lhs.radix+rhs.radix-dst.radix) qubits.
    While this precision issue is not fixed, it's recommedned to use Square instead.
    """

    def _compute_unsigned(self, x: QUFixed, target: QUFixed):
        """Computes square assuming x is unsigned."""
        anc: Qubits = self.alloc_temp_qreg(target.num_qubits, "anc")
        for i in range(x.num_qubits - 1):
            j = 2 * (i - x.radix) + target.radix  # Where in target to write x[i]^2.
            if j >= target.num_qubits:
                break
            skip = 0
            if j < 0:
                skip = -j
                j = 0

            with _SquareIteration().computed(x, anc, i, j, skip):
                qbk.GidneyAdd().compute(target[j:], anc[j:])
        anc.release()

    def _compute(self, x: QFixed, target: QFixed):
        with AbsInPlace().computed(x):
            x_unsigned = QUFixed(x[0 : x.num_qubits - 1], radix=x.radix)
            target_unsigned = QUFixed(target[0 : target.num_qubits - 1], radix=target.radix)
            self._compute_unsigned(x_unsigned, target_unsigned)

    def _estimate(self, x: SymbolicQFixed, target: SymbolicQFixed):
        n = x.num_qubits
        r = x.radix
        assert target.num_qubits == n
        assert target.radix == r

        num_elbows = -3 + 0.5 * n - r + 0.5 * n**2 + n * r - 0.5 * r**2
        cost = QubrickCosts(
            gidney_lelbows=num_elbows,
            gidney_relbows=num_elbows,
            toffs=2 * n - 2,
            local_ancillae=2 * n - 2,
            active_volume=-248.5 + 120.4 * n - 76.5 * r + 30.3 * n**2 + 60.5 * n * r - 24.5 * r**2,
        )
        self.get_qc().add_cost_event(cost)
