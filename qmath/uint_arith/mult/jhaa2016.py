from psiqworkbench import Qubits, QUInt
from psiqworkbench.interoperability import implements
from psiqworkbench.qubricks import Qubrick
from psiqworkbench.symbolics.qubrick_costs import QubrickCosts

from ...utils.gates import ccnot
from ...utils.rotate import rotate_right
from .multiplier import Multiplier


# Computes p+=am*b[1..].
# b[0] must be prepared in zero state and is returned in zero state.
def _add_nop(p: Qubits, b: Qubits, am: Qubits):
    n = len(b) - 1
    assert len(p) == n + 1, "Register sizes must match."
    assert len(am) == 1

    for i in range(n):
        ccnot(am, b[i + 1], p[i])
        b[i].swap(b[i + 1], condition_mask=p[i])
    ccnot(am, b[n], p[n])
    for i in range(n - 1, -1, -1):
        b[i].swap(b[i + 1], condition_mask=p[i])
        ccnot(am, b[i], p[i])


@implements(Multiplier)
class JHHAMultipler(Qubrick):
    """Computes result+=a*b (mod 2^(2n)).

    Requires that registers a and b are of the same size n, and register
    `result` is of size 2n.

    Implementation of the multiplier presented in the paper:
        "Ancilla-Input and Garbage-Output Optimized Design of a Reversible
        Quantum Integer Multiplier",
        Jayashree HV, Himanshu Thapliyal, Hamid R. Arabnia, V K Agrawal, 2016.
        https://arxiv.org/abs/1608.01228
    """

    def _compute(self, a: QUInt, b: QUInt, result: QUInt) -> None:
        n = a.num_qubits
        assert b.num_qubits == n, "Register sizes must match."
        assert result.num_qubits == 2 * n, "Register sizes must match."
        z_cin: Qubits = self.alloc_temp_qreg(1, "anc")
        b1 = z_cin | b

        for i in range(n - 1):
            _add_nop(result[n - 1 : 2 * n], b1, a[i])
            rotate_right(result)
        _add_nop(result[n - 1 : 2 * n], b1, a[n - 1])

        z_cin.release()

    def _estimate(self, a: QUInt, b: QUInt, result: QUInt) -> None:
        n = a.num_qubits
        assert b.num_qubits == n
        assert result.num_qubits == 2 * n

        cost = QubrickCosts(
            toffs=4 * n**2 + n,
            active_volume=204 * n**2 + 47 * n,
            local_ancillae=1,
        )
        self.get_qc().add_cost_event(cost)
