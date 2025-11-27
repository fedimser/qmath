"""
Implementation of adder and multiplier presented in the paper:
   Ancilla-Input and Garbage-Output Optimized Design of a Reversible Quantum Integer Multiplier
   Jayashree HV, Himanshu Thapliyal, Hamid R. Arabnia, V K Agrawal, 2016.
   https://arxiv.org/abs/1608.01228
"""

from psiqworkbench import QUInt
from psiqworkbench.interoperability import implements
from psiqworkbench.qubricks import Qubrick
from ..utils import Qubit, ccnot, controlled_swap, rotate_right

from .multiplier import Multiplier


# Computes p+=am*b[1..].
# b[0] must be prepared in zero state and is returned in zero state.
def _add_nop(p: list[Qubit], b: list[Qubit], am: Qubit):
    n = len(b) - 1
    assert len(p) == n + 1, "Register sizes must match."

    for i in range(n):
        ccnot(am, b[i + 1], p[i])
        controlled_swap(p[i], b[i], b[i + 1])
    ccnot(am, b[n], p[n])
    for i in range(n - 1, -1, -1):
        controlled_swap(p[i], b[i], b[i + 1])
        ccnot(am, b[i], p[i])


@implements(Multiplier)
class JhhaMultipler(Qubrick):
    def _compute(self, a: QUInt, b: QUInt, p: QUInt) -> None:
        """Computes p+=a*b (mod 2^n)."""
        n = len(a)
        assert len(b) == n, "Register sizes must match."
        assert len(p) == 2 * n, "Register sizes must match."
        z_cin: Qubit = Qubit(self.alloc_temp_qreg(1, "anc"))
        b1: list[Qubit] = [z_cin] + Qubit.list(b)

        for i in range(n - 1):
            _add_nop(p[n - 1 : 2 * n], b1, a[i])
            rotate_right(p)
        _add_nop(p[n - 1 : 2 * n], b1, a[n - 1])

        z_cin.release()
