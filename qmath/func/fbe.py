"""Function-value binary expansion algorithms.

Reference:
    Shengbin Wang, Zhimin Wang, Wendong Li, Lixin Fan, Guolong Cui,
    Zhiqiang Wei, Yongjian Gu.
    Quantum circuits design for evaluating transcendental functions based on a
    function-value binary expansion method.
    https://arxiv.org/abs/2001.00807
"""

import math

import psiqworkbench.qubricks as qbk
from psiqworkbench import QFixed, QInt, Qubits, QUFixed, QUInt
from psiqworkbench.qubits.base_qubits import BaseQubits
from psiqworkbench.qubricks import Qubrick
from psiqworkbench.symbolics.qubrick_costs import QubrickCosts

from ..utils.gates import ParallelCnot, ParallelCnotCtrl, write_int
from ..utils.rotate import Div2, rotate_left, rotate_right
from ..utils.symbolic import alloc_temp_qreg_like
from .bits import HighestSetBit
from .common import AddConst, Negate, MultiplyConstAdd
from .sqrt import Sqrt
from .square import Square, SquareOptimized


def _sqrt_half(x: QFixed) -> QFixed:
    op = Sqrt(half_arg=True)
    op.compute(x)
    return op.get_result_qreg()


class Neq(Qubrick):
    """Computes t:=(a!=b)."""

    def _compute(self, t: Qubits, a: Qubits, b: Qubits):
        t.lelbow(a | b)
        a.x()
        b.x()
        t.x(a | b)
        a.x()
        b.x()
        t.x()


class CosFbe(Qubrick):
    """Computes cos(pi*x). Correct for any x.

    Precision of the answer will be about half of `result_radix`.
    """

    def __init__(
        self,
        *,
        result_radix: None | int = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.result_radix = result_radix

    def _compute(self, x: QFixed):
        if self.result_radix is None:
            _, a = alloc_temp_qreg_like(self, x)
        else:
            a = QFixed(self.alloc_temp_qreg(self.result_radix + 2, name="a"), radix=self.result_radix)

        # 0-th iteration: a:= 1 if x[0]==0 else 0.
        x[0].x()
        a[a.radix].x(x[0])
        x[0].x()

        for i in range(1, x.radix):
            # Iteration: a:=sqrt((1±a)/2), sign is minus iff x[i-1]!=x[i].
            t = self.alloc_temp_qreg(1, "t")
            with Neq().computed(t, x[i - 1], x[i]):
                Negate().compute(a, ctrl=t)
                AddConst(1).compute(a)
            a = _sqrt_half(a)
            t.release()

        t = self.alloc_temp_qreg(1, "t")
        with Neq().computed(t, x[x.radix - 1], x[x.radix]):
            Negate().compute(a, ctrl=t)
        t.release()

        self.set_result_qreg(a)

    def _estimate(self, x: QFixed):
        assert self.result_radix is not None

        n = x.radix  # Input radix = number of iterations.
        m = self.result_radix

        ancs = self.alloc_temp_qreg(n * (m + 2), "ancs")
        self.set_result_qreg(ancs[0 : m + 2])

        # This is exactly correct when m%2==0.
        elbows = 0.25 * n * m * m + 4.5 * n * m + 7 * n - 3.5 * m - 0.25 * m**2 - 6
        cost = QubrickCosts(
            gidney_lelbows=elbows,
            gidney_relbows=elbows,
            toffs=2 * n * m + 8 * n - m - 5,
            local_ancillae=m + 10,
            active_volume=18.75 * (n * m**2 - m**2) + 407 * n * m + 886 * n - 301.5 * m - 681,
        )
        self.get_qc().add_cost_event(cost)


class SinFbe(Qubrick):
    """Computes sin(pi*x)=cos(pi*(0.5-x))."""

    def __init__(
        self,
        *,
        result_radix: None | int = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.result_radix = result_radix

    def _compute(self, x: QFixed):
        Negate().compute(x)
        AddConst(0.5).compute(x)
        cos_op = CosFbe(result_radix=self.result_radix)
        cos_op.compute(x)
        self.set_result_qreg(cos_op.get_result_qreg())


class Log2FbeSegment(Qubrick):
    """Computes log2(x) where 1<=x<2.

    Reference: https://arxiv.org/abs/2001.00807, section 3.1.1.
    """

    def _square(self, x: QUFixed) -> QUFixed:
        result = QUFixed(self.alloc_temp_qreg(x.num_qubits, name="a"), radix=x.radix)
        SquareOptimized(signed=False).compute(x, result)
        return result

    def _compute(self, x: QUFixed, result: QUFixed):
        assert x.num_qubits == 2 + x.radix
        assert result.num_qubits == result.radix
        a = self._square(x)

        for i in range(result.radix):
            result_bit = result[result.radix - 1 - i]
            result_bit.x(a[-1])
            Div2().compute(a, ctrl=result_bit)
            a = self._square(a)


class Log2Fbe(Qubrick):
    """Computes log2(x) where x>0."""

    def __init__(
        self,
        *,
        result_radix: None | int = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.result_radix = result_radix

    def _compute(self, x: QUFixed):
        # Find most significant bit of `x`, set it it `msb`.
        xn = x.num_qubits
        msb = self.alloc_temp_qreg(xn, "msb")
        HighestSetBit().compute(x, msb)

        # Make shifted copy of input, such that second most significnat bit in
        # the copy corresponds to highest set bit in input.
        # This way value in x_copy is in range [1, 2).
        x_copy_qubits = self.alloc_temp_qreg(xn, name="x_copy")
        x_copy = QUFixed(x_copy_qubits, radix=xn - 2)
        for i in range(xn):
            # Controlled shift-copy.
            if i == xn - 1:
                ParallelCnotCtrl().compute(msb[i], x[1:], x_copy_qubits[0 : xn - 1])
            else:
                shift_left = xn - 2 - i
                assert shift_left >= 0
                ParallelCnotCtrl().compute(msb[i], x[0 : xn - shift_left], x_copy_qubits[shift_left:])

        # Compute logarithm for shifted copy.
        r = self.result_radix or x.radix
        result_fract_part = QUFixed(self.alloc_temp_qreg(r, "result_frac"), radix=r)
        Log2FbeSegment().compute(x_copy, result_fract_part)

        # Add integer to result, corresponding to input's shift.
        int_part_size = math.ceil(math.log2(max(x.radix, xn - x.radix))) + 1
        result_int_part = QInt(self.alloc_temp_qreg(int_part_size, "result_int"))
        for i in range(xn):
            write_int(result_int_part, i - x.radix, ctrl=msb[i])

        self.set_result_qreg(QFixed(result_fract_part | result_int_part, radix=r))


class LogFbe(Qubrick):
    """Computes logarithm in given base."""

    def __init__(
        self,
        base: float,
        *,
        result_radix: None | int = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.ans_multiplier = 1.0 / math.log2(base)
        self.result_radix = result_radix

    def _compute(self, x: QUFixed):
        op = Log2Fbe(result_radix=self.result_radix)
        with op.computed(x):
            _, ans = alloc_temp_qreg_like(self, op.get_result_qreg())
            if self.ans_multiplier == 1.0:
                ParallelCnot().compute(op.get_result_qreg(), ans)
            else:
                MultiplyConstAdd(self.ans_multiplier).compute(ans, op.get_result_qreg())
        self.set_result_qreg(ans)
