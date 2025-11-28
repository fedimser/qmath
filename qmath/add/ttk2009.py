from typing import Optional

from psiqworkbench import Qubits, QUInt
from psiqworkbench.interfaces import Adder
from psiqworkbench.interoperability import implements
from psiqworkbench.qubricks import Qubrick

from ..utils.qubit import ccnot, cnot


class ApplyOuterTTKAdder(Qubrick):
    def _compute(self, xs: Qubits, ys: Qubits):
        assert len(xs) <= len(ys), "Input register ys must be at least as long as xs."
        for i in range(1, len(xs)):
            cnot(xs[i], ys[i])
        for i in range(len(xs) - 2, 0, -1):
            cnot(xs[i], xs[i + 1])


class ApplyInnerTTKAdderNoCarry(Qubrick):
    def _compute(self, xs: Qubits, ys: Qubits):
        assert len(xs) == len(ys)
        for idx in range(len(xs) - 1):
            ccnot(xs[idx], ys[idx], xs[idx + 1])
        for idx in range(len(xs) - 1, 0, -1):
            cnot(xs[idx], ys[idx])
            ccnot(xs[idx - 1], ys[idx - 1], xs[idx])


class ApplyInnerTTKAdderWithCarry(Qubrick):
    def _compute(self, xs: Qubits, ys: Qubits):
        n = len(xs)
        assert n + 1 == len(ys), "ys must be one qubit longer then xs."
        assert n > 0, "xs should not be empty."
        for idx in range(n - 1):
            ccnot(xs[idx], ys[idx], xs[idx + 1])
        ccnot(xs[n - 1], ys[n - 1], ys[n])
        for idx in range(n - 1, 0, -1):
            cnot(xs[idx], ys[idx])
            ccnot(xs[idx - 1], ys[idx - 1], xs[idx])


@implements(Adder[QUInt, QUInt])
class TTKAdder(Qubrick):
    """Computes lhs += rhs modulo 2^n using ripple-carry addition algorithm.

    Requires len(rhs) <= len(lhs) = n.

    If len(rhs) <= len(lhs)-2, rhs is padded with 0-initialized qubits.

    Implementation of the adder presented in paper:
        "Quantum Addition Circuits and Unbounded Fan-Out",
        Yasuhiro Takahashi, Seiichiro Tani, Noboru Kunihiro, 2009.
        https://arxiv.org/abs/0910.2530
    """

    def _compute(self, lhs: QUInt, rhs: QUInt, ctrl: Optional[Qubits] = None):
        assert ctrl is None, "Control is not supported."
        ys = lhs
        xs = rhs
        rhs_len = len(xs)
        lhs_len = len(ys)

        assert lhs_len >= rhs_len, "Register `lhs` must be longer than register `rhs`."
        assert rhs_len >= 1, "Registers `rhs` and `lhs` must contain at least one qubit."

        if rhs_len == lhs_len:
            if rhs_len > 1:
                ApplyOuterTTKAdder().compute(xs, ys)
                ApplyInnerTTKAdderNoCarry().compute(xs, ys)
                ApplyOuterTTKAdder().compute(xs, ys, dagger=True)
            cnot(xs[0], ys[0])
        elif rhs_len + 1 == lhs_len:
            if rhs_len > 1:
                cnot(xs[rhs_len - 1], ys[lhs_len - 1])
                ApplyOuterTTKAdder().compute(xs, ys)
                ApplyInnerTTKAdderWithCarry().compute(xs, ys)
                ApplyOuterTTKAdder().compute(xs, ys, dagger=True)
            else:
                ccnot(xs[0], ys[0], ys[1])
            cnot(xs[0], ys[0])
        else:
            assert False, "This part is not yet tested."
            assert rhs_len + 2 <= lhs_len
            # Pad xs so that its length is one qubit shorter than ys.
            padding: Qubits = self.alloc_temp_qreg(lhs_len - rhs_len - 1, "padding")
            self._compute(xs | padding, ys)
            padding.release()
