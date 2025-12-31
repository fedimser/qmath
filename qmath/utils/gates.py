from psiqworkbench import Qubits, QUInt, Qubrick, QFixed
from psiqworkbench.symbolics.qubrick_costs import QubrickCosts

from typing import Optional


def cnot(a: Qubits, b: Qubits, ctrl: Optional[Qubits] = None):
    assert len(a) == len(b) == 1
    b.x(a | ctrl)


def ccnot(a: Qubits, b: Qubits, c: Qubits, ctrl: Optional[Qubits] = None):
    assert len(a) == len(b) == len(c) == 1
    c.x(a | b | ctrl)


def write_uint(target: QUInt, number: int, ctrl: Optional[Qubits] = None):
    """Writes target ⊕= number*ctrl."""
    assert 0 <= number < 2**target.num_qubits
    for i in range(target.num_qubits):
        if (number >> i) % 2 == 1:
            target[i].x(ctrl)


def write_qfixed(target: QFixed, number: float, ctrl: Optional[Qubits] = None):
    """Writes target ⊕= number*ctrl."""
    assert 0 <= number < 2**target.num_qubits
    for i in range(target.num_qubits):
        if (number >> i) % 2 == 1:
            target[i].x(ctrl)


class ParallelCnot(Qubrick):
    def _compute(self, a: Qubits, b: Qubits):
        n = a.num_qubits
        assert b.num_qubits == n
        for i in range(n):
            b[i].x(a[i])

    def _estimate(self, a: Qubits, b: Qubits):
        n = a.num_qubits
        assert b.num_qubits == n
        self.get_qc().add_cost_event(QubrickCosts(active_volume=4 * n))
