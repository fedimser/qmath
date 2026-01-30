from typing import Optional

from psiqworkbench import Qubits, Qubrick, QUFixed

from ..utils.gates import swap


class RotateRight(Qubrick):
    """Rotates qubits in register right by 1."""

    def _compute(self, qs: Qubits, ctrl: Optional[Qubits] = None):
        k = len(qs)
        k1 = k // 2
        for i in range(k1):
            swap(qs[i], qs[k - 1 - i], ctrl=ctrl)
        for i in range(k1 - 1 + (k % 2)):
            swap(qs[i], qs[k - 2 - i], ctrl=ctrl)


def rotate_right(qs: Qubits, ctrl: Optional[Qubits] = None):
    """Rotates qubits in register right by 1."""
    RotateRight().compute(qs, ctrl=ctrl)


def rotate_left(qs: Qubits, ctrl: Optional[Qubits] = None):
    """Rotates qubits in register left by 1."""
    RotateRight().compute(qs, ctrl=ctrl, dagger=True)


class Div2(Qubrick):
    """Conditional division by 2.

    Computes x:=x/2 if ctrl=1, else x.
    Allocates one qubit which will unly be freed on uncompute.
    Assumes that input is unsigned.
    """

    def _compute(self, x: QUFixed, ctrl: Optional[Qubits] = None):
        t = self.alloc_temp_qreg(1, "t")
        rotate_right(t | x, ctrl=ctrl)


class Mul2(Qubrick):
    """Conditional multiplication by 2."""

    def _compute(self, x: QUFixed, ctrl: Optional[Qubits] = None):
        t = self.alloc_temp_qreg(1, "t")
        rotate_left(x | t, ctrl=ctrl)
