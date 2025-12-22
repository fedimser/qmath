import numpy as np
import psiqworkbench.qubricks as qbk
from psiqworkbench import QFixed, QUFixed, QUInt, Qubits
from psiqworkbench.qubricks import Qubrick

from ..utils.gates import parallel_cnot


class AbsInPlace(Qubrick):
    """Computes absolute value."""

    def _compute(self, x: QFixed):
        sign = self.alloc_temp_qreg(1, "sign")
        sign.lelbow(x[-1])
        x.x(sign)
        qbk.GidneyAdd().compute(QUInt(x), 1, sign)


class SquareIteration(Qubrick):
    def _compute(self, x: Qubits, anc: Qubits, i, j, skip):
        if skip == 0:
            # print(f"x[{i}]^2 -> ans[{j}]")
            anc[j].x(x[i])
        for ii in range(max(1, skip - 1), 1000):
            anc_pos = j + (ii - skip + 1)
            if (i + ii) >= x.num_qubits or anc_pos >= anc.num_qubits:
                break
            assert 0 <= anc_pos < anc.num_qubits
            # print(f"x[{i}]*x[{i+ii}] -> ans[{anc_pos}]")
            anc[anc_pos].x(x[i] | x[i + ii])


class Square(Qubrick):
    """Computes square of given QFixed register."""

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

    def _compute(self, x: QFixed, target: QFixed, fallback_to_mul=True):
        if fallback_to_mul:
            x_reg = Qubits(x)
            x_copy_reg: Qubits = self.alloc_temp_qreg(x.num_qubits, "x_copy")
            x_copy = QFixed(x_copy_reg, radix=x.radix)
            parallel_cnot(x_reg, x_copy_reg)
            qbk.GidneyMultiplyAdd().compute(target, x, x_copy)
            parallel_cnot(x_reg, x_copy_reg)
            x_copy_reg.release()
            return

        with AbsInPlace().computed(x):
            x_unsigned = QUFixed(x[0 : x.num_qubits - 1], radix=x.radix)
            target_unsigned = QUFixed(target[0 : target.num_qubits - 1], radix=target.radix)
            self._compute_unsigned(x_unsigned, target_unsigned)
