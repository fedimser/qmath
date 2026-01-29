import psiqworkbench.qubricks as qbk
from psiqworkbench import QUInt, Qubits
from psiqworkbench.qubricks import Qubrick


def ctz(n: int) -> int:
    """Counts trailing zeros"""
    assert n > 0
    return (n & -n).bit_length() - 1


def cond_x(control: bool, target: Qubits):
    if control:
        target.x()


class Increment(Qubrick):
    """Increments UInt register by a classical number.

    Reference: https://arxiv.org/abs/2501.07060
    """

    def _add_constant_internal(self, a: int, b: QUInt):
        n = b.num_qubits
        a_bits = [(a >> i) % 2 for i in range(n)]
        assert (a_bits[0] == 1, "a must be odd.")
        if n >= 4:
            c = self.alloc_temp_qreg(n - 3, f"c")
            cond_x(a_bits[1], b[0])
            cond_x(a_bits[1], b[1])
            c[0].lelbow(b[0] | b[1])

            for i in range(2, n - 1):
                cond_x(a_bits[i - 1] ^ a_bits[i], c[i - 2])
                cond_x(a_bits[i], b[i])
                if i != n - 2:
                    c[i - 1].lelbow(c[i - 2] | b[i])
            b[n - 1].x(c[n - 4] | b[n - 2])
            for i in range(n - 2, 1, -1):
                if i != n - 2:
                    b[i + 1].x(c[i - 1])
                    cond_x(a_bits[i], c[i - 1])
                    c[i - 1].relbow(c[i - 2] | b[i])
                cond_x(a_bits[i], c[i - 2])
            b[2].x(c[0])
            cond_x(a_bits[1], c[0])
            c[0].relbow(b[0] | b[1])
            cond_x(a_bits[1], b[0])
            cond_x(a_bits[n - 2] ^ a_bits[n - 1], b[n - 1])
            c.release()
        elif n == 3:
            cond_x(a_bits[1], b[0])
            cond_x(a_bits[1], b[1])
            b[2].x(b[0] | b[1])
            cond_x(a_bits[1], b[0])
            cond_x(a_bits[1] ^ a_bits[2], b[n - 1])
        elif n >= 2:
            cond_x(a_bits[1], b[1])
        if n >= 2:
            b[1].x(b[0])
        b[0].x()

    def _compute(self, lhs: QUInt, rhs: int):
        """Computes lhs+=rhs (mod 2^n)."""
        n = lhs.num_qubits
        rhs %= 2**n
        assert 0 <= rhs < (2**n)
        if rhs == 0:
            return
        tz = ctz(rhs)
        self._add_constant_internal(rhs >> tz, lhs[tz:])
