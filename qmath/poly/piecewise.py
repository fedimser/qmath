from dataclasses import dataclass

from typing import Callable

import numpy as np
import psiqworkbench.qubricks as qbk
from psiqworkbench import QFixed
from psiqworkbench.qubricks import Qubrick

from .remez import remez_piecewise, PiecewisePolynomial
from .horner import HornerScheme


class EvalFunctionPPA(Qubrick):
    """Evaluates function using Piecewise Polynomial Approximation.

    Arguments:
        f - function to approximate.
        interval - interval on which to approximate.
        degree - degree of polynomials used to approximate the function.
        error_tol - maximal error between true function and its apprimxation.


    Reference:
        Thomas Haner, Martin Roetteler, Krysta M. Svore.
        Optimizing Quantum Circuits for Arithmetic. 2018.
        https://arxiv.org/abs/1805.12445
    """

    def __init__(
        self,
        f: Callable[[float], float],
        *,
        interval: tuple[float, float],
        degree: int,
        error_tol: float,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.poly = remez_piecewise(f, interval, degree, error_tol)

    def _compute(self, x: QFixed):
        if len(self.poly.pieces) == 1:
            hs = HornerScheme(self.poly.pieces[0].coefs)
            hs.compute(x)
            self.set_result_qreg(hs.get_result_qreg())
            return

        # TODO: implement case with multiple pieces.
        assert False, "Not implemented."
