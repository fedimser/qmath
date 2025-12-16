"""Becnhmarks.

Here we run resource estimates for some Qubrikcs and store them in benchmarks.csv.
We compute number of auxiliary qubits and total number of operations.
There is also an automatic test checking that these resource estimates don't change.
This allows us to detect regressions and quantify optimizations.
"""

from dataclasses import dataclass

import psiqworkbench.qubricks as qbk
from psiqworkbench import QPU, QFixed, QUInt

from qmath.add import CDKMAdder, TTKAdder
from qmath.mult import Square

BENCHMARKS_FILE_NAME = "qmath/benchmarks/benchmarks.csv"


@dataclass(frozen=True)
class BenchmarkResult:
    name: str  # Interval start.
    qubits: int  # Number of auxiliary qubits (not counting input and output registers).
    ops: int  # Number of operations.

    @staticmethod
    def csv_header():
        return ",".join(["Benchmark", "Qubits", "Ops"])

    def to_csv_row(self):
        return f"{self.name},{self.qubits},{self.ops}"


def _benhmark_gidney_add() -> BenchmarkResult:
    qpu = QPU(filters=[">>witness>>"])
    qpu.reset(100)
    qs_x = QFixed(32, radix=24, qpu=qpu)
    qs_y = QFixed(32, radix=24, qpu=qpu)
    qbk.GidneyAdd().compute(qs_x, qs_y)
    metrics = qpu.metrics()
    return BenchmarkResult(name="GidneyAdd", qubits=metrics["qubit_highwater"] - 64, ops=metrics["total_num_ops"])


def _benhmark_cdkm_adder() -> BenchmarkResult:
    qpu = QPU(filters=[">>witness>>"])
    qpu.reset(100)
    qs_x = QUInt(32, qpu=qpu)
    qs_y = QUInt(32, qpu=qpu)
    CDKMAdder().compute(qs_x, qs_y)
    metrics = qpu.metrics()
    return BenchmarkResult(name="CDKMAdder", qubits=metrics["qubit_highwater"] - 64, ops=metrics["total_num_ops"])


def _benhmark_ttk_adder() -> BenchmarkResult:
    qpu = QPU(filters=[">>witness>>"])
    qpu.reset(100)
    qs_x = QUInt(32, qpu=qpu)
    qs_y = QUInt(32, qpu=qpu)
    TTKAdder().compute(qs_x, qs_y)
    metrics = qpu.metrics()
    return BenchmarkResult(name="TTKAdder", qubits=metrics["qubit_highwater"] - 64, ops=metrics["total_num_ops"])


def _benhmark_square() -> BenchmarkResult:
    qpu = QPU(filters=[">>witness>>"])
    qpu.reset(200)
    qs_x = QFixed(32, name="x", radix=24, qpu=qpu)
    qs_y = QFixed(32, name="y", radix=24, qpu=qpu)
    Square().compute(qs_x, qs_y)
    metrics = qpu.metrics()
    return BenchmarkResult(name="Square", qubits=metrics["qubit_highwater"] - 64, ops=metrics["total_num_ops"])


def _run_benchmarks() -> str:
    """Runs all benchmarks, returns results as CSV table."""
    results = [
        _benhmark_gidney_add(),
        _benhmark_cdkm_adder(),
        _benhmark_ttk_adder(),
        _benhmark_square(),
    ]
    return "\n".join([BenchmarkResult.csv_header()] + [r.to_csv_row() for r in results])


def test_benchmarks():
    with open(BENCHMARKS_FILE_NAME, "r") as f:
        golden = f.read()
    actual = _run_benchmarks()
    error_message = (
        "Resource estimates for benchmarks changed. "
        "If these changes are expected, update them by running: "
        "python3 ./qmath/benchmarks/update.py"
    )
    assert actual == golden, error_message
