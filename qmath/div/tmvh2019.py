import psiqworkbench.qubricks as qbk
from psiqworkbench import Qubits, QUInt
from psiqworkbench.interfaces import Adder
from psiqworkbench.qubricks import Qubrick
from psiqworkbench.symbolics.qubrick_costs import QubrickCosts

from ..utils.gates import cnot
from ..utils.padding import padded


class TMVHDivider(Qubrick):
    """Quantum divder. Computes (a, b, c) := (a%b, b, a/b).

    Constraints:
     * len(a) == len(c) == n.
     * len(b) <= len(a).
     * b != 0.
     * c must be initialized to zeros.

    Implementation of 2 division algorithms presented in the paper:
        "Quantum Circuit Designs of Integer Division Optimizing T-count and T-depth",
        Thapliyal, Munoz-Coreas, Varun, Humble, 2019.
        https://arxiv.org/pdf/1809.09732.

    Args:
        restoring (bool): Whether to use "restoring" or "non-restoring" division algorithm.
                          Non-restoring is the default.
        adder (Adder): in-place adder to use in this divider.
    """

    def __init__(self, *, restoring: bool = False, adder: Adder = qbk.GidneyAdd(), **kwargs):
        super().__init__(**kwargs)
        self.restoring = restoring
        self.adder = adder

    def _ctrl_add(self, ctrl: Qubits, xs: Qubits, ys: Qubits):
        """Computes ys+=xs if ctrl=1, does nothing if ctrl=0."""
        assert len(ctrl) == 1
        self.adder.compute(ys, xs, ctrl=ctrl)

    def _subtract(self, xs: Qubits, ys: Qubits):
        """Computes ys -= xs by reducing problem to addition."""
        ys.x()
        self.adder.compute(ys, xs)
        ys.x()

    def _add_sub(self, ctrl: Qubits, xs: Qubits, ys: Qubits):
        """Computes ys-=xs if ctrl=1, and ys+=xs if ctrl=0."""
        for i in range(len(ys)):
            cnot(ctrl, ys[i])
        self.adder.compute(ys, xs)
        for i in range(len(ys)):
            cnot(ctrl, ys[i])

    def _divide_restoring(self, a: Qubits, b: Qubits, c: Qubits):
        """Computes (a, b, c) := (a%b, b, a/b).

        Constraints:
         * a,b,c must have the same number of qubits n.
         * 0 <= a < 2^n.
         * 0 < b < 2^(n-1).
         * c must be initialized to zeros.
        """
        n = len(a)
        assert len(b) == n, "Registers sizes must match."
        assert len(c) == n, "Registers sizes must match."

        for i in range(1, n + 1):
            y = a[n - i : n]
            if n != i:
                y = y | c[0 : n - i]
            self._subtract(b, y)
            cnot(y[n - 1], c[n - i])
            self._ctrl_add(c[n - i], b, y)
            c[n - i].x()

    def _divide_non_restoring(self, a: Qubits, b: Qubits, c: Qubits):
        """Computes (a[0..n-2], [a[n-1]]+c, b) := (a%b, a/b, b).

        Constraints:
         * a and b must have n qubits, c must have size n-1 qubits.
         * 0 <= a < 2^n.
         * 0 < b < 2^(n-1).
         * c must be initialized to zeros.
        """
        n = len(a)
        assert len(b) == n, "Registers sizes are incompatible."
        assert len(c) == n - 1, "Registers sizes are incompatible."

        r = a[0 : n - 1]
        q = a[n - 1] | c
        self._subtract(b, q)
        for i in range(1, n):
            q[n - i].x()
            Y = r[n - 1 - i : n - 1] | q[0 : n - i]
            self._add_sub(q[n - i], b, Y)
        self._ctrl_add(q[0], b[0 : n - 1], r)
        q[0].x()

    def _compute(self, a: QUInt, b: QUInt, c: QUInt):
        """Computes (a, b, c) := (a%b, b, a/b)."""
        n = len(a)
        assert len(b) <= len(a), "Register b must be no longer than register a."
        assert len(c) == len(a), "Register c must have the same lenth as register a."

        if self.restoring:
            n = max(len(a), len(b) + 1)
            with padded(self, (a, b, c), (n, n, n)) as (a, b, c):
                self._divide_restoring(a, b, c)
        else:
            n = max(len(a), len(b) + 1)
            with padded(self, (a, b, c), (n, n - 1, n)) as (a, b, c):
                self._divide_non_restoring(a, b | c[0], c[1:])
                a[n - 1].swap(c[0])

    def _estimate(self, a: QUInt, b: QUInt, c: QUInt):
        na = a.num_qubits
        nb = b.num_qubits
        assert c.num_qubits == na

        # TODO: implement.
        cost = QubrickCosts()
        self.get_qc().add_cost_event(cost)
