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
        # Computes ax + k.
        def linear(a: QFixed, k: QFixed) -> QFixed:
            result = QFixed(self.alloc_temp_qreg(x.num_qubits, "a"), radix=x.radix)
            qbk.GidneyMultiplyAdd().compute(result, a, x)
            qbk.GidneyAdd().compute(result, k)
            return result

        a = QFixed(self.alloc_temp_qreg(x.num_qubits, "a"), radix=x.radix)
        a.write(self.coefs[-1])
        for k in self.coefs[:-1][::-1]:
            a = linear(a, k)
        self.set_result_qreg(a)
