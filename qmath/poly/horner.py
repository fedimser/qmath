from psiqworkbench import QFixed
from psiqworkbench.qubricks import Qubrick

from ..func.common import AddConst, MultiplyAdd
from ..utils.symbolic import alloc_temp_qreg_like


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
            _, result = alloc_temp_qreg_like(self, x, name="result")
            MultiplyAdd().compute(result, a, x)
            AddConst().compute(result, b)
            return result

        # TODO: skip allocating first register by doing with quantum-classical multiplication on first step.
        _, a = alloc_temp_qreg_like(self, x, name="a")
        a.write(self.coefs[-1])
        for b in self.coefs[:-1][::-1]:
            a = linear(a, b)
        self.set_result_qreg(a)
