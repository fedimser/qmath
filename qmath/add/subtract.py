import psiqworkbench.qubricks as qbk
from psiqworkbench import QFixed, QInt
from psiqworkbench.qubricks import Qubrick

from .increment import Increment


class Subtract(Qubrick):
    # TODO: implement more efficiently.
    def _negate(self, x: QFixed):
        x_as_int = QInt(x)
        x_as_int.x()
        Increment().compute(x_as_int, 1)

    # TODO: implement more efficiently.i
    # Warning: messes up rhs.
    def _compute(self, lhs: QFixed, rhs: QFixed):
        """Computes lhs-= rhs. Negates rhs in the process."""
        assert lhs.num_qubits == lhs.num_qubits
        assert lhs.radix == rhs.radix
        self._negate(rhs)
        qbk.GidneyAdd().compute(lhs, rhs)
