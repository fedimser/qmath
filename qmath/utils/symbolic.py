from psiqworkbench import QFixed, Qubits, Qubrick, SymbolicQubits
from psiqworkbench.symbolics import Parameter


class SymbolicQFixed(SymbolicQubits):
    """Symbolic register for fixed-precision signed number."""

    def __init__(self, *, radix: Parameter | int = 0, **kwargs):
        super().__init__(**kwargs)
        self.radix = radix


def alloc_temp_qreg_like(qbk: Qubrick, x: QFixed, name: str = "") -> tuple[Qubits, QFixed]:
    """Allocates temporary register with the same size and radix as x.

    Supports symbolic computation.

    Returns pair of (Qubits, QFixed).
      Qubits result can be used to call release() if you need to release this register explicitly.
      QFixed result can be used in furthr computation.
    """
    if name == "":
        name = x.name + "_clone"
    if x.qpu.is_symbolic:
        qreg = qbk.alloc_temp_qreg(x.num_qubits, name)
        qreg.radix = x.radix
        # Hacky but works.
        return qreg, qreg
    else:
        qreg = qbk.alloc_temp_qreg(x.num_qubits, name)
        return qreg, QFixed(qreg, radix=x.radix, qpu=x.qpu)
