# From https://github.com/fedimser/quant-arith-re/blob/main/lib/src/QuantumArithmetic/CDKM2004.qs
# https://arxiv.org/pdf/quant-ph/0410184
# Unoptimized version
# TODO: complete implementation (incl. optimized version + control).

from typing import Optional

from psiqworkbench import Qubits
from psiqworkbench.interfaces import Adder
from psiqworkbench.interoperability import implements
from psiqworkbench.qubricks import Qubrick

from ..utils import Qubit, ccnot, cnot


def MAJ(a: Qubit, b: Qubit, c: Qubit):
    cnot(c, b)
    cnot(c, a)
    ccnot(a, b, c)


def UMA_v1(a: Qubits, b: Qubits, c: Qubits):
    # Do some changes...
    ccnot(a, b, c)
    cnot(c, a)
    cnot(a, b)


@implements(Adder[Qubits, Qubits])
class CdkmAdder(Qubrick):
    def _compute(self, lhs: Qubits, rhs: Qubits, ctrl: Optional[Qubits] = None):
        assert isinstance(lhs, Qubits)
        assert isinstance(rhs, Qubits)
        assert ctrl is None, "Control not yet supported."

        n = len(rhs)
        assert len(lhs) == n

        C = self.alloc_temp_qreg(1, "C")

        MAJ(C, lhs[0], rhs[0])
        for i in range(1, n):
            MAJ(rhs[i - 1], lhs[i], rhs[i])
        for i in range(n - 1, 0, -1):
            UMA_v1(rhs[i - 1], lhs[i], rhs[i])
        UMA_v1(C, lhs[0], rhs[0])

        C.release()
