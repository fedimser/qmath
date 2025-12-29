import psiqworkbench.qubricks as qbk
from psiqworkbench import QFixed, Qubrick
from psiqworkbench.symbolics.qubrick_costs import QubrickCosts


class CompareConstGT(Qubrick):
    """Computes (x > value) where value is classical constant."""

    def __init__(self, value: float, **kwargs):
        super().__init__(**kwargs)
        self.value = value

    def _compute(self, x: QFixed):
        cmp = qbk.CompareGT()
        cmp.compute(x, self.value)
        self.set_result_qreg(cmp.get_result_qreg())

    def _estimate(self, x: QFixed):
        # This RE is not always correct because after _nudge_classical_compare,
        # shifting by radix and taking integer part, there might be some
        # trailing zeros. In which case we should subtract number of trailing
        # zeros frin num_elbows. However, we can't write number of trailing
        # zeros as a function of symbolic radix.
        # If x is not finite binary fraction, ntz=O(1) and this discrepancy is
        # small.
        num_elbows = x.num_qubits - 1
        ancs = self.alloc_temp_qreg(num_elbows, "ancs")
        self.set_result_qreg(ancs[num_elbows - 1])
        cost = QubrickCosts(
            active_volume=52 * num_elbows,
            gidney_lelbows=num_elbows,
        )
        self.get_qc().add_cost_event(cost)
