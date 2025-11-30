from psiqworkbench import QFixed
from psiqworkbench.qubricks import Qubrick

import psiqworkbench.qubricks as qbk


class HornerScheme(Qubrick):
    """Evaluates polynomial using Horner scheme.

    Given x in input regsiter, evaluates sum(coefs[i] * x**i) in result register.
    """

    def __init__(self, coefs: list[float], **kwargs):
        super().__init__(**kwargs)
        self.coefs = coefs

    def _compute(self, x: QFixed):
        # Computes ax + b.
        def linear(a: QFixed, b: float) -> QFixed:
            result = QFixed(self.alloc_temp_qreg(x.num_qubits, "a"), radix=x.radix)
            qbk.GidneyMultiplyAdd().compute(result, a, x)
            if abs(b) > 1e-15:
                qbk.GidneyAdd().compute(result, b)
            return result

        # TODO: skip allocating first register by doing with quantum-classical multiplication on first step.
        a = QFixed(self.alloc_temp_qreg(x.num_qubits, "a"), radix=x.radix)
        a.write(self.coefs[-1])
        for b in self.coefs[:-1][::-1]:
            a = linear(a, b)
        self.set_result_qreg(a)
