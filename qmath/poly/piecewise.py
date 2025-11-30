import math
from dataclasses import dataclass
from typing import Callable

import numpy as np
import psiqworkbench.qubricks as qbk
from psiqworkbench import QFixed, QUInt
from psiqworkbench.qubricks import Qubrick

from ..utils.gates import write_uint
from ..utils.lookup import TableLookup
from .horner import HornerScheme
from .remez import remez_piecewise


# Converts signed real number to unsigned integer whose binary representation is
# identical to that of given number if written to given QFixed register.
def real_as_uint(number: float, register: QFixed):
    ans = int(round(number * (2 ** (register.radix))))
    assert -(2 ** (register.num_qubits - 1)) <= ans < 2 ** (register.num_qubits - 1)
    if ans < 0:
        ans += 2**register.num_qubits
    assert 0 <= ans < 2**register.num_qubits
    return ans


class WritePieceNumber(Qubrick):
    """Identifies number of a segment in which x lies and writes it to `target`.

    Let len(points)=n. They split number line into n+1 intervals:
      * Interval 0: (-∞, points[0]].
      * Interval i: (points[i-1], points[i]] for i=1..n-1.
      * Interval n: (points[n], +∞).

    This qubrick identifies the interval number by doing n sequential
    comparisons and writes the result as unsigned integer to `target`.
    """

    def _compute(self, x: QFixed, target: QUInt, points: list[int]):
        assert len(points) + 1 <= 2**target.num_qubits
        assert points == sorted(points)

        for i, split_point in enumerate(points):
            comparator = qbk.CompareGT()
            comparator.compute(x, split_point)
            result = comparator.get_result_qreg()
            write_uint(target, (i + 1) ^ i, ctrl=result)
            comparator.uncompute()


class EvalFunctionPPA(Qubrick):
    """Evaluates function using Piecewise Polynomial Approximation.

    Arguments:
        f - function to approximate.
        interval - interval on which to approximate.
        degree - degree of polynomials used to approximate the function.
        error_tol - maximal error between true function and its apprimxation.

    Reference:
        Thomas Haner, Martin Roetteler, Krysta M. Svore.
        Optimizing Quantum Circuits for Arithmetic. 2018.
        https://arxiv.org/abs/1805.12445
    """

    def __init__(
        self,
        f: Callable[[float], float],
        *,
        interval: tuple[float, float],
        degree: int,
        error_tol: float,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.poly = remez_piecewise(f, interval, degree, error_tol)
        self.num_pieces = len(self.poly.pieces)
        self.deg = max(len(p.coefs) for p in self.poly.pieces) - 1

    def _label(self, x: QFixed) -> QUInt:
        # Computes the number of the piece inside which x is.
        # Figure 1 in the paper.
        # All x to the left of piece 0 will fall into piece 0.
        # All x to the right of the last piece will fall into the last piece.
        num_pieces = len(self.poly.pieces)
        label_size = int(math.ceil(math.log2(num_pieces)))
        l = QUInt(self.alloc_temp_qreg(label_size, "l"))
        points = [self.poly.pieces[i].b for i in range(self.num_pieces - 1)]
        WritePieceNumber().compute(x, l, points)
        return l

    def _compute(self, x: QFixed):
        if self.num_pieces == 1:
            hs = HornerScheme(self.poly.pieces[0].coefs)
            hs.compute(x)
            self.set_result_qreg(hs.get_result_qreg())
            return
        # Compute which piece x is in.
        l = self._label(x)

        # Prepare coefficients.
        assert x.num_qubits <= 64  # So we can use np.int128 to represent coefficients.
        a = np.zeros((self.num_pieces, self.deg + 1), dtype=np.int64)
        for i, piece in enumerate(self.poly.pieces):
            for j, coef in enumerate(piece.coefs):
                a[i][j] = real_as_uint(coef, x)

        # Allocate register for the answer and write highest coefficient there.
        ans = QFixed(self.alloc_temp_qreg(x.num_qubits, "ans"), radix=x.radix)
        TableLookup().compute(l, QUInt(ans), a[:, self.deg])

        # Allocate register to write coefficients.
        q_coefs = QFixed(self.alloc_temp_qreg(x.num_qubits, "coefs"), radix=x.radix)
        q_coefs_as_uint = QUInt(q_coefs)

        # Parallel Horner scheme.
        for i in range(self.deg - 1, -1, -1):
            # Write coefficients to register qa.
            coefs = a[:, i]
            if i < self.deg - 1:
                coefs ^= a[:, i + 1]
            TableLookup().compute(l, q_coefs_as_uint, coefs)

            # Compute ans := ans * x + coef.
            next_ans = QFixed(self.alloc_temp_qreg(x.num_qubits, f"ans{i}"), radix=x.radix)
            qbk.GidneyMultiplyAdd().compute(next_ans, ans, x)
            qbk.GidneyAdd().compute(next_ans, q_coefs)
            ans = next_ans

        self.set_result_qreg(ans)
