"""Function-value binary expansion algorithms.

Reference:
    Shengbin Wang, Zhimin Wang, Wendong Li, Lixin Fan, Guolong Cui,
    Zhiqiang Wei, Yongjian Gu.
    Quantum circuits design for evaluating transcendental functions based on a
    function-value binary expansion method.
    https://arxiv.org/abs/2001.00807
"""

import psiqworkbench.qubricks as qbk
from psiqworkbench import QFixed, QInt, Qubits, QUInt
from psiqworkbench.qubits.base_qubits import BaseQubits
from psiqworkbench.qubricks import Qubrick
from psiqworkbench.symbolics.qubrick_costs import QubrickCosts

from .common import AddConst, Negate
from .sqrt import Sqrt
from ..utils.symbolic import alloc_temp_qreg_like


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
