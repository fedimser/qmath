import psiqworkbench.qubricks as qbk
from psiqworkbench import QFixed, QInt, QUInt, Qubits
from psiqworkbench.qubricks import Qubrick

from ..mult.square import square


# TODO: implement more efficiently and move to common.
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


class _InitialGuess(Qubrick):
    def _msb(self, a: Qubits, ans: Qubits):
        """Finds most significant bit in a and sets it in ans."""
        flag: Qubits = self.alloc_temp_qreg(1, "t")

        # For each input qubit i compute which output qubit must be set if i is MSB.
        for i in range(a.num_qubits - 1, -1, -1):
            # Copy a[i] to ans[j], but only if flag is unset.
            flag.x()
            ans[i].x(a[i] | flag)
            flag.x()

            # If ans[i]=1 (which implies flag was unset), set the flag.
            # All less significant qubits will be ignored.
            flag.x(ans[i])

    def _compute(self, a: QFixed, ans: QFixed):
        """Computes ans := 2**(-(floor(log2(a)))//2)."""
        # TODO: can this be optimized to compute result directly into ans?
        r = self.alloc_temp_qreg(a.num_qubits, "r")
        self._msb(a, r)

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


class _NewtonIteration(Qubrick):
    """Computes x1 := x0*(1.5-a*x0^2).

    Here a is half of argument to inverse square root.
    """

    def _compute(self, x0: QFixed, x1: QFixed, a: QFixed, c=1.5):
        t1 = QFixed(self.alloc_temp_qreg(x0.num_qubits, "t1"), radix=x0.radix)
        t2 = QFixed(self.alloc_temp_qreg(x0.num_qubits, "t2"), radix=x0.radix)
        t3 = QFixed(self.alloc_temp_qreg(x0.num_qubits, "t3"), radix=x0.radix)
        square(x0, t1, self)  # t1 := x0^2.
        qbk.GidneyMultiplyAdd().compute(t2, a, t1)  # t2 := a*x0^2.
        t3.write(c)
        subtract(t3, t2)  # t3 := c - a*x0^2
        qbk.GidneyMultiplyAdd().compute(x1, x0, t3)  # x1 := x0*(c-a*x0^2).


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
        a_half = QFixed(a, radix=a.radix + 1)
        n = self.num_iterations
        x = [QFixed(self.alloc_temp_qreg(a.num_qubits, f"x_{i}"), radix=a.radix) for i in range(n + 1)]
        print("a=", a.read())
        _InitialGuess().compute(a, x[0])
        print("x0=", x[0].read())
        for i in range(1, n + 1):
            c = 1.615 if i == 0 else 1.5
            _NewtonIteration().compute(x[i - 1], x[i], a_half, c=c)
            print(f"x{i}=", x[i].read())

        self.set_result_qreg(x[n])
