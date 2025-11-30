from psiqworkbench import Qubits, QUInt

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


def parallel_cnot(a: Qubits, b: Qubits):
    n = len(a)
    assert len(b) == n
    for i in range(n):
        b[i].x(a[i])
