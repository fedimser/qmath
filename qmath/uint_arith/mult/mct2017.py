from psiqworkbench import Qubits, QUInt
from psiqworkbench.interoperability import implements
from psiqworkbench.qubricks import Qubrick
from psiqworkbench.symbolics.qubrick_costs import QubrickCosts

from ...utils.gates import ccnot, cnot
from .multiplier import Multiplier


# Controlled addition, described in section III of the paper.
def _ctrl_add(ctrl: Qubits, a: Qubits, b: Qubits, z0: Qubits, z1: Qubits):
    n = len(a)
    assert len(b) == n, "Size mismatch."
    assert len(ctrl) == 1
    assert len(z0) == 1
    assert len(z1) == 1

    # Step 1.
    for i in range(1, n):
        cnot(a[i], b[i])

    # Step 2.
    ccnot(ctrl, a[n - 1], z0)
    for i in range(n - 2, 0, -1):
        cnot(a[i], a[i + 1])

    # Step 3.
    for i in range(0, n - 1):
        ccnot(b[i], a[i], a[i + 1])

    # Step 4.
    ccnot(b[n - 1], a[n - 1], z1)
    ccnot(ctrl, z1, z0)
    ccnot(b[n - 1], a[n - 1], z1)
    ccnot(ctrl, a[n - 1], b[n - 1])

    # Step 5.
    for i in range(n - 2, -1, -1):
        ccnot(b[i], a[i], a[i + 1])
        ccnot(ctrl, a[i], b[i])

    # Step 6.
    for i in range(1, n - 1):
        cnot(a[i], a[i + 1])

    # Step 7.
    for i in range(1, n):
        cnot(a[i], b[i])


@implements(Multiplier)
class MCTMultipler(Qubrick):
    """Computes result+=a*b (mod 2^(2n)).

    Requires that size of result register is equal to sum of sizes of input
    registers.

    Implementation of the multiplier presented in paper:
        "T-count Optimized Design of Quantum Integer Multiplication",
        Edgard Muñoz-Coreas, Himanshu Thapliyal, 2017.
        https://arxiv.org/abs/1706.05113
    """

    def _compute(self, a: QUInt, b: QUInt, result: QUInt) -> None:
        n1 = len(a)
        n2 = len(b)
        assert len(result) == n1 + n2, "Size mismatch."
        anc: Qubits = self.alloc_temp_qreg(1, "anc")
        p: Qubits = result | anc

        # Step 1.
        for i in range(n1):
            ccnot(b[0], a[i], p[i])

        # Steps 2-3.
        for i in range(1, n2):
            _ctrl_add(b[i], a, p[i : i + n1], p[i + n1], p[i + n1 + 1])

        anc.release()

    def _estimate(self, a: QUInt, b: QUInt, result: QUInt) -> None:
        n = a.num_qubits
        assert b.num_qubits == n
        assert result.num_qubits == 2 * n

        cost = QubrickCosts(
            toffs=3 * n**2 - 2,
            active_volume=157 * n**2 - 40 * n - 70,
            local_ancillae=1,
        )
        self.get_qc().add_cost_event(cost)
