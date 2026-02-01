"""Functions to apply permutations."""

from psiqworkbench import Qubits, QUFixed
from psiqworkbench.qubricks import Qubrick

from typing import Optional

from .gates import swap


class RotateLeftByOne(Qubrick):
    """Rotates qubits in register right by 1."""

    def _compute(self, qs: Qubits, ctrl: Optional[Qubits] = None):
        k = len(qs)
        k1 = k // 2
        for i in range(k1):
            swap(qs[i], qs[k - 1 - i], ctrl=ctrl)
        for i in range(k1 - 1 + (k % 2)):
            swap(qs[i], qs[k - 2 - i], ctrl=ctrl)


def rotate_left(qs: Qubits, ctrl: Optional[Qubits] = None):
    """Rotates qubits in register right by 1."""
    RotateLeftByOne().compute(qs, ctrl=ctrl)


def rotate_right(qs: Qubits, ctrl: Optional[Qubits] = None):
    """Rotates qubits in register left by 1."""
    RotateLeftByOne().compute(qs, ctrl=ctrl, dagger=True)


class Div2(Qubrick):
    """Conditional division by 2.

    Computes x:=x/2 if ctrl=1, else x.
    Allocates one qubit which will only be freed on uncompute.
    Assumes that input is unsigned.
    """

    def _compute(self, x: QUFixed, ctrl: Optional[Qubits] = None):
        t = self.alloc_temp_qreg(1, "t")
        rotate_left(t | x, ctrl=ctrl)


class Mul2(Qubrick):
    """Conditional multiplication by 2."""

    def _compute(self, x: QUFixed, ctrl: Optional[Qubits] = None):
        t = self.alloc_temp_qreg(1, "t")
        rotate_right(x | t, ctrl=ctrl)


class ApplyPermutation(Qubrick):
    """Applies given permutation to qubits by doing SWAPs."""

    def __init__(self, perm: list[int], **kwargs):
        super().__init__(**kwargs)
        self.n = len(perm)
        assert sorted(perm) == list(range(self.n)), f"Not a valid permutation: {perm}."

        self.cycles = []
        used = [False] * self.n
        for i in range(self.n):
            if used[i]:
                continue
            cycle = []
            while not used[i]:
                cycle.append(i)
                used[i] = True
                i = perm[i]
            if len(cycle) >= 2:
                self.cycles.append(cycle)

    @staticmethod
    def _index_qubits(x: Qubits, idx: list[int]) -> Qubits:
        ans = x[idx[0]]
        for i in range(1, len(idx)):
            ans = ans | x[idx[i]]
        return ans

    def _compute(self, x: Qubits, ctrl: Optional[Qubits] = None):
        assert x.num_qubits == self.n, "Register has wrong number of qubits"
        for cycle in self.cycles:
            rotate_left(ApplyPermutation._index_qubits(x, cycle), ctrl=ctrl)


class RotateRight(Qubrick):
    """Rotates qubit register right by specified number of qubits.

    Rotation is in right direction, i.e. towards higher bits for little-endian numbers.
    """

    def __init__(self, shift: int, **kwargs):
        super().__init__(**kwargs)
        self.shift = shift

    def _compute(self, x: Qubits, ctrl: Optional[Qubits] = None):
        n = x.num_qubits
        perm = [(i - self.shift) % n for i in range(n)]
        ApplyPermutation(perm).compute(x, ctrl=ctrl)
