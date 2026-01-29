import numpy as np
import pytest
from psiqworkbench import QPU, QFixed, QUInt
from psiqworkbench.filter_presets import BIT_DEFAULT

from qmath.utils.test_utils import QPUTestHelper
from qmath.poly import WritePieceNumber, EvalPiecewisePolynomial, PiecewisePolynomial, Piece, EvalFunctionPPA


def test_write_piece_number():
    qpu = QPU(filters=BIT_DEFAULT)
    qpu.reset(30)
    qx = QFixed(10, name="qx", radix=5, qpu=qpu)
    target = QUInt(3, qpu=qpu)
    split_points = [-7.5, -6.5, -2.25, 0, 0.5, 6.0]

    def _check(x, expected_result):
        qx.write(x)
        target.write(0)
        func = WritePieceNumber()
        func.compute(qx, target, split_points)
        assert target.read() == expected_result

    for i, x in enumerate(split_points):
        _check(x - 0.1, i)
        _check(x, i)
        _check(x + 0.1, i + 1)


def test_eval_piecewise_polynomial():
    poly = PiecewisePolynomial(
        [
            Piece(-1, 0, [1, 1, 1, 0]),
            Piece(0, 1.5, [1, -2, -2.5, 0]),
            Piece(1.5, 2.5, [5.875, -3, -5.5, 1]),
        ]
    )
    qpu = QPU(filters=BIT_DEFAULT)
    for x in [-1, 1.5, 2]:
        qpu.reset(150)
        qx = QFixed(8, name="qx", radix=3, qpu=qpu)
        qx.write(x)
        func = EvalPiecewisePolynomial(poly)
        func.compute(qx)
        result = func.get_result_qreg().read()
        assert result == poly.eval(x)


@pytest.mark.smoke
def test_eval_linear():
    qpu = QPU(filters=BIT_DEFAULT)
    qpu.reset(100)
    qs_x = QFixed(8, name="x", radix=3, qpu=qpu)
    qs_x.write(2.5)
    func = EvalFunctionPPA(lambda x: 1.5 * x + 1, interval=(-1, 1), degree=1, error_tol=1e-10)
    func.compute(qs_x)
    result = func.get_result_qreg().read()
    assert result == 4.75


@pytest.mark.slow
def test_eval_sin():
    qpu_helper = QPUTestHelper(num_qubits=500, qubits_per_reg=20, radix=15, num_inputs=1)
    q_x = qpu_helper.inputs[0]
    func = EvalFunctionPPA(np.sin, interval=(-1, 1), degree=3, error_tol=1e-4)
    func.compute(q_x)
    qpu_helper.record_op(func.get_result_qreg())

    for x in np.linspace(-1, 1, 21):
        result = qpu_helper.apply_op([x])
        assert np.abs(result - np.sin(x)) < 1.4e-4


def test_eval_sin_odd():
    qpu = QPU(filters=BIT_DEFAULT)
    func = EvalFunctionPPA(np.sin, interval=(-1, 1), degree=2, error_tol=1e-3, is_odd=True)
    assert len(func.poly.pieces) == 1
    for x in [0.5]:
        qpu.reset(500)
        qx = QFixed(12, name="qx", radix=10, qpu=qpu)
        qx.write(x)
        func.compute(qx)
        result = func.get_result_qreg().read()
        assert np.abs(result - np.sin(x)) < 1e-3


def test_eval_cos_even():
    qpu = QPU(filters=BIT_DEFAULT)
    func = EvalFunctionPPA(np.cos, interval=(-1, 1), degree=2, error_tol=1e-3, is_even=True)
    assert len(func.poly.pieces) == 1
    for x in [0.5]:
        qpu.reset(500)
        qx = QFixed(12, name="qx", radix=10, qpu=qpu)
        qx.write(x)
        func.compute(qx)
        result = func.get_result_qreg().read()
        assert np.abs(result - np.cos(x)) < 1e-3
