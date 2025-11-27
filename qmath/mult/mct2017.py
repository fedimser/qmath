"""
Implementation of the multiplier presented in paper:
   T-count Optimized Design of Quantum Integer Multiplication
   Edgard Muñoz-Coreas, Himanshu Thapliyal, 2017.
   https://arxiv.org/pdf/1706.05113
"""

from psiqworkbench import QUInt
from psiqworkbench.qubricks import Qubrick
from psiqworkbench.interoperability import implements

from ..utils import cnot, ccnot, Qubit
from .multiplier import Multiplier


# Controlled addition, described in section III of the paper.
def _ctrl_add(ctrl: Qubit, a: list[Qubit], b: list[Qubit], z0: Qubit, z1: Qubit):
    n = len(a)
    assert len(b) == n, "Size mismatch."

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
class MctMultipler(Qubrick):
    def _compute(self, a: QUInt, b: QUInt, c: QUInt) -> None:
        n1 = len(a)
        n2 = len(b)
        assert len(c) == n1 + n2, "Size mismatch."
        anc: Qubit = Qubit(self.alloc_temp_qreg(1, "anc"))
        p: list[Qubit] = Qubit.list(c) + [anc]

        # Step 1.
        for i in range(n1):
            ccnot(b[0], a[i], p[i])

        # Steps 2-3.
        for i in range(1, n2):
            _ctrl_add(b[i], a, p[i : i + n1], p[i + n1], p[i + n1 + 1])

        anc.release()
