from typing import Optional

from psiqworkbench import Qubits, QUInt
from psiqworkbench.interfaces import Adder
from psiqworkbench.interoperability import implements
from psiqworkbench.qubricks import Qubrick
from psiqworkbench.symbolics.qubrick_costs import QubrickCosts

from ..utils.padding import padded


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

    def _cnot(self, a: Qubits, b: Qubits):
        b.x(a | self.ctrl)

    def _ccnot(self, a: Qubits, b: Qubits, c: Qubits):
        c.x(a | b | self.ctrl)

    def _maj(self, a: Qubits, b: Qubits, c: Qubits):
        self._cnot(c, b)
        self._cnot(c, a)
        self._ccnot(a, b, c)

    # UnMajority and Add (2-CNOT version).
    def _uma_v1(self, a: Qubits, b: Qubits, c: Qubits):
        self._ccnot(a, b, c)
        self._cnot(c, a)
        self._cnot(a, b)

    # Simple (unoptimized) version of the adder, from §2.
    # Computes b:=(a+b)%(2^n); z⊕=(a+b)/(2^n).
    def _add_simple(self, a: Qubits, b: Qubits, z: Qubits):
        n = len(a)
        assert len(b) == n, "Register sizes must match."
        assert len(z) == 1
        c = self.alloc_temp_qreg(1, "c")

        self._maj(c, b[0], a[0])
        for i in range(1, n):
            self._maj(a[i - 1], b[i], a[i])
        self._cnot(a[n - 1], z)
        for i in range(n - 1, 0, -1):
            self._uma_v1(a[i - 1], b[i], a[i])
        self._uma_v1(c, b[0], a[0])

        c.release()

    # Optimized adder, from §3.
    # Computes b:=(a+b)%(2^n); z⊕=(a+b)/(2^n).
    def _add_optimized(self, a: Qubits, b: Qubits, z: Qubits):
        n = len(a)
        assert len(b) == n, "Register sizes must match."
        assert n >= 4, "n must be at least 4."
        assert len(z) == 1
        c = self.alloc_temp_qreg(1, "c")

        for i in range(1, n):
            b[i].x(a[i])
        self._cnot(a[1], c)
        self._ccnot(a[0], b[0], c)
        self._cnot(a[2], a[1])
        self._ccnot(c, b[1], a[1])
        self._cnot(a[3], a[2])
        for i in range(2, n - 2):
            self._ccnot(a[i - 1], b[i], a[i])
            self._cnot(a[i + 2], a[i + 1])
        self._ccnot(a[n - 3], b[n - 2], a[n - 2])
        self._cnot(a[n - 1], z)
        self._ccnot(a[n - 2], b[n - 1], z)
        for i in range(1, n - 1):
            b[i].x()
        self._cnot(c, b[1])
        for i in range(2, n):
            self._cnot(a[i - 1], b[i])
        self._ccnot(a[n - 3], b[n - 2], a[n - 2])
        for i in range(n - 3, 1, -1):
            self._ccnot(a[i - 1], b[i], a[i])
            self._cnot(a[i + 2], a[i + 1])
            b[i + 1].x()
        self._ccnot(c, b[1], a[1])
        self._cnot(a[3], a[2])
        b[2].x()
        self._ccnot(a[0], b[0], c)
        self._cnot(a[2], a[1])
        b[1].x()
        self._cnot(a[1], c)
        self._cnot(a[0], b[0])
        for i in range(1, n):
            b[i].x(a[i])

        c.release()

    def _compute(self, lhs: QUInt, rhs: QUInt, ctrl: Optional[Qubits] = None):
        self.ctrl = ctrl
        assert len(lhs) >= len(rhs), "Register `rhs` cannot be longer than register `lhs`."
        n = len(rhs)
        if len(lhs) == n:
            # Addition modulo 2^n.
            if n >= 5 and self.optimized:
                self._add_optimized(rhs[0 : n - 1], lhs[0 : n - 1], lhs[n - 1])
            elif n >= 2:
                self._add_simple(rhs[0 : n - 1], lhs[0 : n - 1], lhs[n - 1])
            self._cnot(rhs[n - 1], lhs[n - 1])
        elif len(lhs) == n + 1:
            # Addition with carry.
            if n >= 4 and self.optimized:
                self._add_optimized(rhs, lhs[0:n], lhs[n])
            else:
                self._add_simple(rhs, lhs[0:n], lhs[n])
        else:
            assert len(rhs) < len(lhs) - 1
            with padded(self, (rhs,), (len(lhs) - 1,)) as (rhs,):
                assert len(rhs) == len(lhs) - 1
                self._compute(lhs, rhs)

    def _estimate(self, lhs: QUInt, rhs: QUInt, ctrl: Optional[Qubits] = None):
        assert self.optimized, "RE implemented only for optimized version."
        assert lhs.num_qubits == rhs.num_qubits, "RE implemented only for inputs of equal size."
        n = lhs.num_qubits
        # Note: this RE is correct only for n>=5.

        if ctrl is None:
            cost = QubrickCosts(
                toffs=2 * n - 3,
                active_volume=114 * n - 169,
                local_ancillae=1,
            )
        else:
            cost = QubrickCosts(
                gidney_lelbows=2 * n - 3,
                gidney_relbows=2 * n - 3,
                toffs=5 * n - 6,
                active_volume=341 * n - 445,
                local_ancillae=2,
            )
        self.get_qc().add_cost_event(cost)
