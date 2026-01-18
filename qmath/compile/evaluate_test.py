import os
from dataclasses import dataclass
from typing import Callable
import pytest

from psiqworkbench import QPU, QFixed
from psiqworkbench.filter_presets import BIT_DEFAULT

from qmath.compile import EvaluateExpression
from qmath.utils.test_utils import QPUTestHelper

RUN_SLOW_TESTS = os.getenv("RUN_SLOW_TESTS") == "1"


@dataclass
class EvaluateTestCase:
    expr: str
    args: list[str]
    func: Callable[..., float]
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
        assert qpu_helper.apply_op(args) == tc.func(*args)


# Use this test case for debugging. It does not use any helpers.
@pytest.mark.skipif(not RUN_SLOW_TESTS, reason="slow test")
def test_debug():
    qpu = QPU(filters=BIT_DEFAULT)
    qpu.reset(1000)
    qs_x = QFixed(20, name="x", radix=5, qpu=qpu)
    qs_y = QFixed(20, name="y", radix=5, qpu=qpu)
    qs_z = QFixed(20, name="z", radix=5, qpu=qpu)
    x, y, z = -10, 0, 5
    qs_x.write(x)
    qs_y.write(y)
    qs_z.write(z)

    expected = -x + 2 * (y + 3 * z - x * x) + x * y + x * y * z - z * x
    compiler = EvaluateExpression("-x + 2*(y + 3*z - x*x) + x*y + x*y*z - z*x", qc=qpu)
    compiler.compute({"x": qs_x, "y": qs_y, "z": qs_z})
    ans = compiler.get_result_qreg()

    assert ans.read() == expected


def test_add():
    _test_evaluate(
        EvaluateTestCase(
            expr="x+y+z",
            args=["x", "y", "z"],
            func=lambda x, y, z: x + y + z,
            inputs=[[1, 2, -1], [-3.5, 4, 0]],
            num_qubits=50,
        )
    )


def test_sub_classical_quantum():
    _test_evaluate(
        EvaluateTestCase(
            expr="5-x",
            args=["x"],
            func=lambda x: 5 - x,
            inputs=[[-1.25], [0], [5], [11.5]],
            num_qubits=50,
            radix=2,
        )
    )


def test_multiply():
    _test_evaluate(
        EvaluateTestCase(
            expr="x*y",
            args=["x", "y"],
            func=lambda x, y: x * y,
            inputs=[[3, 2], [-3.5, 4]],
            num_qubits=100,
        )
    )


def test_multiply_const():
    _test_evaluate(
        EvaluateTestCase(
            expr="x*2.5",
            args=["x"],
            func=lambda x: x * 2.5,
            inputs=[[-1], [0], [2], [4]],
            num_qubits=100,
        )
    )


@pytest.mark.skipif(not RUN_SLOW_TESTS, reason="slow test")
def test_complex_expression():
    _test_evaluate(
        EvaluateTestCase(
            expr="-x + 2*(y + 3*z - x*x) + x*y + x*y*z - z*x",
            args=["x", "y", "z"],
            func=lambda x, y, z: -x + 2 * (y + 3 * z - x * x) + x * y + x * y * z - z * x,
            inputs=[[1, 2.0, -3], [4.125, 5, 6.5], [-10, 0, 5]],
            num_qubits=300,
            qubits_per_reg=20,
            radix=10,
        )
    )
