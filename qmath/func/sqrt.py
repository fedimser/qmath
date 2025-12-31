import psiqworkbench.qubricks as qbk
from psiqworkbench import QFixed, Qubits, QUFixed
from psiqworkbench.qubricks import Qubrick
from psiqworkbench.symbolics.qubrick_costs import QubrickCosts

from ..func.common import AbsInPlace, MultiplyAdd
from ..utils.gates import ParallelCnot
from ..utils.symbolic import SymbolicQFixed, alloc_temp_qreg_like


class Sqrt(Qubrick):
    """Computes sqrt(x).

    If half_arg=True, coomputes sqrt(x/2).

    Uses qbk.Sqrt (which is designed for QUInt and halves result size) and then
    adds padding qubits so the output has the same size as input.
    """

    def __init__(
        self,
        *,
        half_arg=False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.half_arg = half_arg

    def _compute(self, x: QFixed) -> QFixed:
        assert x.radix >= 0
        op = qbk.Sqrt()
        n_left_pad = x.radix // 2
        if self.half_arg:
            if x.radix % 2 == 0:
                pad = self.alloc_temp_qreg(1, "pad")
                op.compute(pad | x)
                pad.release()
                n_left_pad -= 1
            else:
                op.compute(x)
        else:
            if x.radix % 2 == 0:
                op.compute(x)
            else:
                pad = self.alloc_temp_qreg(1, "pad")
                op.compute(pad | x)
                pad.release()
        ans = op.get_result_qreg()

        left_pad = None
        if n_left_pad > 0:
            left_pad = self.alloc_temp_qreg(n_left_pad, "left_pad")

        right_pad = None
        n_right_pad = x.num_qubits - (n_left_pad + ans.num_qubits)
        assert n_right_pad >= 0
        if n_right_pad > 0:
            right_pad = self.alloc_temp_qreg(n_right_pad, "right_pad")

        self.set_result_qreg(QFixed(left_pad | ans | right_pad, radix=x.radix))
