import psiqworkbench.qubricks as qbk
from psiqworkbench import QUInt
from psiqworkbench.qubricks import Qubrick


class Increment(Qubrick):
    """Increments UInt register by a classical number.

    Currently implemented with GidneyAdd, TODO: implement with https://arxiv.org/abs/2501.07060
    """

    def _compute(self, lhs: QUInt, rhs: int):
        """Computes lhs+=rhs (mod 2^n)."""
        n = lhs.num_qubits
        rhs %= 2**n
        assert 0 <= rhs < (2**n)
        qbk.GidneyAdd().compute(lhs, rhs)
