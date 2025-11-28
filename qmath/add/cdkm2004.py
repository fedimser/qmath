from typing import Optional

from psiqworkbench import Qubits, QUInt
from psiqworkbench.interfaces import Adder
from psiqworkbench.interoperability import implements
from psiqworkbench.qubricks import Qubrick

from ..utils.qubit import Qubit, ccnot, cnot


def _maj(a: Qubit, b: Qubit, c: Qubit):
    cnot(c, b)
    cnot(c, a)
    ccnot(a, b, c)


# UnMajority and Add (2-CNOT version).
def _uma_v1(a: Qubit, b: Qubit, c: Qubit):
    ccnot(a, b, c)
    cnot(c, a)
    cnot(a, b)


# Simple (unoptimized) version of the adder, from §2.
# Computes b:=(a+b)%(2^n); z⊕=(a+b)/(2^n).
def _add_simple(qbk: Qubrick, a: list[Qubit], b: list[Qubit], z: Qubit):
    n = len(a)
    assert len(b) == n, "Register sizes must match."
    c = Qubit(qbk.alloc_temp_qreg(1, "c"))

    _maj(c, b[0], a[0])
    for i in range(1, n):
        _maj(a[i - 1], b[i], a[i])
    cnot(a[n - 1], z)
    for i in range(n - 1, 0, -1):
        _uma_v1(a[i - 1], b[i], a[i])
    _uma_v1(c, b[0], a[0])

    c.release()


# Optimized adder, from §3.
# Computes b:=(a+b)%(2^n); z⊕=(a+b)/(2^n).
def _add_optimized(qbk: Qubrick, a: list[Qubit], b: list[Qubit], z: Qubit):
    n = len(a)
    assert len(b) == n, "Register sizes must match."
    assert n >= 4, "n must be at least 4."
    c = Qubit(qbk.alloc_temp_qreg(1, "c"))

    for i in range(1, n):
        cnot(a[i], b[i])
    cnot(a[1], c)
    ccnot(a[0], b[0], c)
    cnot(a[2], a[1])
    ccnot(c, b[1], a[1])
    cnot(a[3], a[2])
    for i in range(2, n - 2):
        ccnot(a[i - 1], b[i], a[i])
        cnot(a[i + 2], a[i + 1])
    ccnot(a[n - 3], b[n - 2], a[n - 2])
    cnot(a[n - 1], z)
    ccnot(a[n - 2], b[n - 1], z)
    for i in range(1, n - 1):
        b[i].x()
    cnot(c, b[1])
    for i in range(2, n):
        cnot(a[i - 1], b[i])
    ccnot(a[n - 3], b[n - 2], a[n - 2])
    for i in range(n - 3, 1, -1):
        ccnot(a[i - 1], b[i], a[i])
        cnot(a[i + 2], a[i + 1])
        b[i + 1].x()
    ccnot(c, b[1], a[1])
    cnot(a[3], a[2])
    b[2].x()
    ccnot(a[0], b[0], c)
    cnot(a[2], a[1])
    b[1].x()
    cnot(a[1], c)
    for i in range(n):
        cnot(a[i], b[i])

    c.release()


@implements(Adder[QUInt, QUInt])
class CDKMAdder(Qubrick):
    """Computes lhs += rhs.

    Sizes of registers must match or lhs must be 1 qubit longer.

    Implementation of the adder presented in paper:
        "A new quantum ripple-carry addition circuit",
        Cuccaro, Draper, Kutin, Moulton, 2004.
        https://arxiv.org/abs/quant-ph/0410184
    """

    def __init__(self, *, optimized: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.optimized = optimized

    def _compute(self, lhs: QUInt, rhs: QUInt, ctrl: Optional[Qubits] = None):
        assert ctrl is None, "Control is not supported."
        assert len(lhs) >= len(rhs), "Register `lhs` must be longer than register `rhs`."
        n = len(rhs)
        if len(lhs) == n:
            # Addition modulo 2^n.
            if n >= 5 and self.optimized:
                _add_optimized(self, rhs[0 : n - 1], lhs[0 : n - 1], lhs[n - 1])
            elif n >= 2:
                _add_simple(self, rhs[0 : n - 1], lhs[0 : n - 1], lhs[n - 1])
            cnot(rhs[n - 1], lhs[n - 1])
        elif len(lhs) == n + 1:
            # Addition with carry.
            if n >= 4 and self.optimized:
                _add_optimized(self, rhs, lhs[0:n], lhs[n])
            else:
                _add_simple(self, rhs, lhs[0:n], lhs[n])
        else:
            assert len(lhs) > len(rhs) + 1
            padding: Qubits = self.alloc_temp_qreg(len(lhs) - len(rhs) - 1, "padding")
            self._compute(lhs, rhs | padding)
            padding.release()
