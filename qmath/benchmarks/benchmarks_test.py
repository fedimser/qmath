"""Becnhmarks.

Here we run resource estimates for some Qubrikcs and store them in benchmarks.csv.
We compute number of auxiliary qubits and total number of operations.
There is also an automatic test checking that these resource estimates don't change.
This allows us to detect regressions and quantify optimizations.
"""

from dataclasses import dataclass

import psiqworkbench.qubricks as qbk
from psiqworkbench import QPU, QFixed, QUInt

from qmath.add import CDKMAdder, TTKAdder, Subtract, Increment
from qmath.mult import Square
from qmath.func import InverseSquareRoot

BENCHMARKS_FILE_NAME = "qmath/benchmarks/benchmarks.csv"


BENCHMARK_FILTERS = [
    ">>witness>>",
]


@dataclass(frozen=True)
class BenchmarkResult:
    name: str  # Interval start.
    metrics: dict  # QPU metrics.

    @staticmethod
    def csv_header():
        return ",".join(["Benchmark", "Qubits", "Ops", "Toffoli", "T"])

    def to_csv_row(self):
        return ",".join(
            [
                self.name,
                str(self.metrics["qubit_highwater"]),
                str(self.metrics["total_num_ops"]),
                str(self.metrics["toffoli_count"]),
                str(self.metrics["t_count"]),
            ]
        )


def _benhmark_gidney_add() -> BenchmarkResult:
    qpu = QPU(filters=BENCHMARK_FILTERS)
    qpu.reset(100)
    qs_x = QFixed(32, radix=24, qpu=qpu)
    qs_y = QFixed(32, radix=24, qpu=qpu)
    qbk.GidneyAdd().compute(qs_x, qs_y)
    return BenchmarkResult(name="GidneyAdd", metrics=qpu.metrics())


def _benhmark_cdkm_adder() -> BenchmarkResult:
    qpu = QPU(filters=BENCHMARK_FILTERS)
    qpu.reset(100)
    qs_x = QUInt(32, qpu=qpu)
    qs_y = QUInt(32, qpu=qpu)
    CDKMAdder().compute(qs_x, qs_y)
    return BenchmarkResult(name="CDKMAdder", metrics=qpu.metrics())


def _benhmark_ttk_adder() -> BenchmarkResult:
    qpu = QPU(filters=BENCHMARK_FILTERS)
    qpu.reset(100)
    qs_x = QUInt(32, qpu=qpu)
    qs_y = QUInt(32, qpu=qpu)
    TTKAdder().compute(qs_x, qs_y)
    return BenchmarkResult(name="TTKAdder", metrics=qpu.metrics())


def _benchmark_square(fallback_to_mul: bool) -> BenchmarkResult:
    qpu = QPU(filters=BENCHMARK_FILTERS)
    qpu.reset(200)
    qs_x = QFixed(32, name="x", radix=24, qpu=qpu)
    qs_y = QFixed(32, name="y", radix=24, qpu=qpu)
    Square(fallback_to_mul=fallback_to_mul).compute(qs_x, qs_y)
    name = "Square(via mul)" if fallback_to_mul else "Square"
    return BenchmarkResult(name=name, metrics=qpu.metrics())


def _benhmark_subtract() -> BenchmarkResult:
    qpu = QPU(filters=BENCHMARK_FILTERS)
    qpu.reset(200)
    qs_x = QFixed(32, name="x", radix=24, qpu=qpu)
    qs_y = QFixed(32, name="y", radix=24, qpu=qpu)
    Subtract().compute(qs_x, qs_y)
    return BenchmarkResult(name="Subtract", metrics=qpu.metrics())


def _benchmark_inv_square_root() -> BenchmarkResult:
    qpu = QPU(filters=BENCHMARK_FILTERS)
    qpu.reset(400)
    qs_a = QFixed(20, name="a", radix=15, qpu=qpu)
    InverseSquareRoot(num_iterations=3).compute(qs_a)
    return BenchmarkResult(name="InvSquareRoot(iter=3)", metrics=qpu.metrics())


def _benhmark_increment() -> BenchmarkResult:
    qpu = QPU(filters=[">>toffoli-filter>>", ">>witness>>"])
    qpu.reset(64)
    qs_x = QUInt(32, name="x", qpu=qpu)
    Increment().compute(qs_x, 1)
    return BenchmarkResult(name="IncBy1", metrics=qpu.metrics())


def _run_benchmarks() -> str:
    """Runs all benchmarks, returns results as CSV table."""
    results = [
        _benhmark_gidney_add(),
        _benhmark_cdkm_adder(),
        _benhmark_ttk_adder(),
        _benchmark_square(False),
        _benchmark_square(True),
        _benhmark_subtract(),
        _benchmark_inv_square_root(),
        _benhmark_increment(),
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


# Use this for development when optimizing/debugging single benchmark.
# python3 ./qmath/benchmarks/benchmarks_test.py
if __name__ == "__main__":
    result = _benhmark_increment()
    print(result.to_csv_row())
