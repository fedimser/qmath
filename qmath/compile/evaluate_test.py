from dataclasses import dataclass
from typing import Callable

from psiqworkbench import QPU, QFixed
from psiqworkbench.filter_presets import BIT_DEFAULT

from qmath.compile import EvaluateExpression
from qmath.utils.test_utils import QPUTestHelper


@dataclass
class EvaluateTestCase:
    expr: str
    args: list[str]
    func: Callable[[list[float]], float]
    inputs: list[list[float]]
    num_qubits: int
    qubits_per_reg: int = 8
    radix: int = 1


def _test_evaluate(tc: EvaluateTestCase):
    qpu_helper = QPUTestHelper(
        num_inputs=len(tc.args),
        num_qubits=tc.num_qubits,
        qubits_per_reg=tc.qubits_per_reg,
        radix=tc.radix,
    )
    v = {tc.args[i]: qpu_helper.inputs[i] for i in range(len(tc.args))}
    op = EvaluateExpression(tc.expr, qc=qpu_helper.qpu)
    op.compute(v)
    qpu_helper.record_op(op.get_result_qreg())

    for args in tc.inputs:
        assert qpu_helper.apply_op(args) == tc.func(args)


# Use this test case for debugging. It does not use any helpers.
def test_debug():
    qpu = QPU(filters=BIT_DEFAULT)
    qpu.reset(200)
    qs_x = QFixed(10, name="x", radix=5, qpu=qpu)
    qs_y = QFixed(10, name="y", radix=5, qpu=qpu)
    qs_x.write(2)
    qs_y.write(3)

    compiler = EvaluateExpression("x*y", qc=qpu)
    compiler.compute({"x": qs_x, "y": qs_y})
    ans = compiler.get_result_qreg()

    assert ans.read() == 6


def test_add():
    _test_evaluate(
        EvaluateTestCase(
            expr="x+y+z",
            args=["x", "y", "z"],
            func=lambda a: a[0] + a[1] + a[2],
            inputs=[[1, 2, -1], [-3.5, 4, 0]],
            num_qubits=50,
        )
    )


def test_multiply():
    _test_evaluate(
        EvaluateTestCase(
            expr="x*y",
            args=["x", "y"],
            func=lambda a: a[0] * a[1],
            inputs=[[3, 2], [-3.5, 4]],
            num_qubits=100,
        )
    )
