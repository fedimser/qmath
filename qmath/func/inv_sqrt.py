import psiqworkbench.qubricks as qbk
from psiqworkbench import QFixed, QInt, QUInt, Qubits
from psiqworkbench.qubricks import Qubrick

from ..mult.square import square


def negate(x: QFixed):
    x_as_int = QInt(x)
    x_as_int.x()
    qbk.GidneyAdd().compute(x_as_int, 1)


# TODO: implement more efficiently and move to common.
# Warning: messes up rhs.
def subtract(lhs: QFixed, rhs: QFixed):
    """Computes lhs-= rhs."""
    assert lhs.num_qubits == lhs.num_qubits
    assert lhs.radix == rhs.radix
    negate(rhs)
    qbk.GidneyAdd().compute(lhs, rhs)


class _NewtonIteration(Qubrick):
    """Computes x1 := x0*(1.5-a*x0^2).

    Here a is half of argument to inverse square root.
    """

    def _compute(self, x0: QFixed, x1: QFixed, a: QFixed):
        t1 = QFixed(self.alloc_temp_qreg(x0.num_qubits, "t1"), radix=x0.radix)
        t2 = QFixed(self.alloc_temp_qreg(x0.num_qubits, "t2"), radix=x0.radix)
        t3 = QFixed(self.alloc_temp_qreg(x0.num_qubits, "t3"), radix=x0.radix)
        square(x0, t1, self)  # t1 := x0^2.
        qbk.GidneyMultiplyAdd().compute(t2, a, t1)  # t2 := a*x0^2.
        t3.write(1.5)
        subtract(t3, t2)  # t3 := 1.5 - a*x0^2
        qbk.GidneyMultiplyAdd().compute(x1, x0, t3)  # x1 := x0*(1.5-a*x0^2).


class InverseSquareRoot(Qubrick):
    """Evaluates function f(a)=a^-0.5.

    Uses Newton-Raphson iteration with good inital guess.

    Reference:
        Thomas Haner, Martin Roetteler, Krysta M. Svore.
        Optimizing Quantum Circuits for Arithmetic. 2018.
        https://arxiv.org/abs/1805.12445
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
        # TODO: implement.
        self.set_result_qreg(a)
