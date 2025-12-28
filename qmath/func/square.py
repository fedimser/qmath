import numpy as np
import psiqworkbench.qubricks as qbk
from psiqworkbench import QFixed, QUFixed, QUInt, Qubits
from psiqworkbench.qubricks import Qubrick
from psiqworkbench.qubits.base_qubits import BaseQubits
from psiqworkbench.symbolics.qubrick_costs import QubrickCosts

from ..func.common import AbsInPlace, MultiplyAdd
from ..utils.symbolic import alloc_temp_qreg_like
from ..utils.gates import ParallelCnot


class SquareIteration(Qubrick):
    def _compute(self, x: Qubits, anc: Qubits, i: int, j: int, skip: int):
        if skip == 0:
            anc[j].lelbow(x[i])
        for i2 in range(max(1, skip - 1), x.num_qubits - i):
            anc_pos = j + (i2 - skip + 1)
            if anc_pos >= anc.num_qubits:
                break
            assert 0 <= anc_pos < anc.num_qubits
            anc[anc_pos].lelbow(x[i] | x[i + i2])


class Square(Qubrick):
    """Computes square of given QFixed register.

    There are 2 versions:
      * If fallback_to_mul=True (default), makes a copy of input and uses
          GidneyMultiplyAdd.
      * If fallback_to_mul=False, uses specialized squaring algorithm.
          This option uses 2x less resources but requires ~1 extra qubit to achieve
          the same precision as square via multiplication.
          This is because it doesn't add padding qubits so result.radix=x.radix*2,
          like the multiplication does.
    """

    def __init__(self, *, fallback_to_mul: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.fallback_to_mul = fallback_to_mul

    def _compute_unsigned(self, x: QUFixed, target: QUFixed):
        """Computes square assuming x is unsigned.

        Uses algorithm from Lemma 6 in https://arxiv.org/pdf/2105.12767.
        """
        anc: Qubits = self.alloc_temp_qreg(target.num_qubits, "anc")
        for i in range(x.num_qubits - 1):
            j = 2 * (i - x.radix) + target.radix  # Where in target to write x[i]^2.
            if j >= target.num_qubits:
                break
            skip = 0
            if j < 0:
                skip = -j
                j = 0

            with SquareIteration().computed(x, anc, i, j, skip):
                qbk.GidneyAdd().compute(target[j:], anc[j:])
        anc.release()

    def _compute(self, x: QFixed, target: QFixed):
        if self.fallback_to_mul:
            x_copy_reg, x_copy = alloc_temp_qreg_like(self, x)
            print(f"{x_copy.num_qubits=} {x_copy.radix=} {x_copy_reg.num_qubits=}")
            with ParallelCnot().computed(x, x_copy):
                MultiplyAdd().compute(target, x, x_copy)
            x_copy_reg.release()
            return

        with AbsInPlace().computed(x):
            x_unsigned = QUFixed(x[0 : x.num_qubits - 1], radix=x.radix)
            target_unsigned = QUFixed(target[0 : target.num_qubits - 1], radix=target.radix)
            self._compute_unsigned(x_unsigned, target_unsigned)
