"""Functions to apply permutations."""

from psiqworkbench import Qubits
from psiqworkbench.qubricks import Qubrick

from typing import Optional

from .rotate import rotate_right


def _index_qubits(x: Qubits, idx: list[int]) -> Qubits:
    ans = x[idx[0]]
    for i in range(1, len(idx)):
        ans = ans | x[idx[i]]
    return ans


class ApplyPermutation(Qubrick):
    """Applies given permutation to qubits by doing SWAPs."""

    def __init__(
        self,
        perm: list[int],
        **kwargs,
    ):
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

    def _compute(self, x: Qubits, ctrl: Optional[Qubits] = None):
        assert x.num_qubits == self.n, "Register has wrong number of qubits"
        for cycle in self.cycles:
            rotate_right(_index_qubits(x, cycle), ctrl=ctrl)
