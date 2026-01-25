import psiqworkbench.qubricks as qbk
from psiqworkbench import QFixed, QInt, QUInt, Qubits
from psiqworkbench.qubricks import Qubrick
from psiqworkbench.qubits.base_qubits import BaseQubits
from psiqworkbench.symbolics.qubrick_costs import QubrickCosts

from .square import Square
from .common import Subtract, MultiplyAdd
from ..utils.symbolic import alloc_temp_qreg_like
from .bits import HighestSetBit


class _InitialGuess(Qubrick):

    def _compute(self, a: QFixed, ans: QFixed):
        """Computes ans := 2**(-(floor(log2(a)))//2)."""
        # TODO: can this be optimized to compute result directly into ans?
        r = self.alloc_temp_qreg(a.num_qubits, "r")
        HighestSetBit().compute(a, r)

        for i in range(a.num_qubits - 1, -1, -1):
            pos1 = i - a.radix
            pos2 = (-pos1) // 2
            j = pos2 + ans.radix
            if j < 0:
                raise ValueError("Increase radix of ans.")
            if j >= ans.num_qubits - 1:
                # Ignore this.
                # Very small inputs, for which result overflows, result in answer 0.
                continue
            assert 0 <= j < ans.num_qubits - 1
            ans[j].x(r[i])

    def _estimate(self, a: QFixed, ans: QFixed):
        # This resource estimate is correct only when radix is between 1/3 and 2/3 of num_qubits.
        n = a.num_qubits
        assert a.num_qubits == ans.num_qubits, "Input and output size must match for RE."
        self.alloc_temp_qreg(1, "flag")
        self.alloc_temp_qreg(n, "r")
        cost = QubrickCosts(
            active_volume=52 * n,
            gidney_lelbows=n,
        )
        self.get_qc().add_cost_event(cost)


class _NewtonIteration(Qubrick):
    """Computes x1 := x0*(1.5-a*x0^2).

    Here a is half of argument to inverse square root.
    """

    def _compute(self, x0: QFixed, x1: QFixed, a: QFixed, c=1.5):
        _, t1 = alloc_temp_qreg_like(self, x0, name="t1")
        _, t2 = alloc_temp_qreg_like(self, x0, name="t2")
        _, t3 = alloc_temp_qreg_like(self, x0, name="t3")
        Square().compute(x0, t1)  # t1 := x0^2.
        MultiplyAdd().compute(t2, t1, a)  # t2 := a*x0^2.
        t3.write(c)
        Subtract().compute(t3, t2)  # t3 := c - a*x0^2
        MultiplyAdd().compute(x1, x0, t3)  # x1 := x0*(c-a*x0^2).


# TODO: simplify RE for qubit_highwater using rewriters.
# See https://github.com/PsiQ/bartiq/blob/main/docs/tutorials/2025_ieee_qw/04_rewriters.ipynb
class InverseSquareRoot(Qubrick):
    """Evaluates function f(a)=a^-0.5.

    Uses Newton-Raphson iteration with good inital guess.

    Reference:
        Thomas Haner, Martin Roetteler, Krysta M. Svore.
        Optimizing Quantum Circuits for Arithmetic. 2018.
        https://arxiv.org/abs/1805.12445

    We use simplified version of algorithm:
        * First iteration is not optimized.
        * First iteration's constant C is taken 1.615 regardless of a.

    See https://github.com/fedimser/qmath/blob/main/notebooks/classic/inv_sqrt.ipynb
    """

    def __init__(
        self,
        *,
        num_iterations=3,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.num_iterations = num_iterations

    def _compute(self, a: QFixed):
        n = self.num_iterations
        x = [alloc_temp_qreg_like(self, a, name=f"x_{i}")[1] for i in range(n + 1)]
        _InitialGuess().compute(a, x[0])
        a.radix = a.radix + 1  # a := a/2.
        for i in range(1, n + 1):
            c = 1.615 if i == 1 else 1.5
            _NewtonIteration().compute(x[i - 1], x[i], a, c=c)
        self.set_result_qreg(x[n])
