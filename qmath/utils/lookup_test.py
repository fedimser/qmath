import random

import pytest
from psiqworkbench import QPU, QUInt, SymbolicQPU, SymbolicQubits, resource_estimator
from psiqworkbench.filter_presets import BIT_DEFAULT
from psiqworkbench.resource_estimation.qre._resource_dict import ResourceDict
from psiqworkbench.symbolics import Parameter

from qmath.utils.lookup import TableLookup
from qmath.utils.re_utils import FILTERS_FOR_NUMERIC_RE, verify_re


@pytest.mark.smoke
def test_table_lookup():
    tables = [[1, 8, 7, 9, 15, 0, 3, 4], [8, 4, 9, 0, 0, 1, 1]]
    qpu = QPU(filters=BIT_DEFAULT)
    qpu.reset(9)
    address = QUInt(3, name="address", qpu=qpu)
    target = QUInt(4, name="target", qpu=qpu)
    for table in tables:
        op = TableLookup(table)
        for i in range(len(table)):
            address.write(i)
            target.write(0)
            op.compute(address, target)
            assert target.read() == table[i]


def _re_symbolic_lookup(op: TableLookup) -> ResourceDict:
    n = Parameter("n", "Target size")
    m = op.address_size
    qpu = SymbolicQPU()
    address = SymbolicQubits(m, "address", qpu)
    target = SymbolicQubits(n, "target", qpu)
    op.compute(address, target)
    return resource_estimator(qpu).resources()


def _re_numeric_lookup(op: TableLookup, assgn: dict[str, int]) -> ResourceDict:
    n = assgn["n"]
    m = op.address_size
    qpu = QPU(filters=FILTERS_FOR_NUMERIC_RE)
    qpu.reset(2 * n + m)
    address = QUInt(m, "address", qpu)
    target = QUInt(n, "target", qpu)
    op.compute(address, target)
    return resource_estimator(qpu).resources()


@pytest.mark.re
def test_re_table_lookup():
    for table_size, n in [(2, 10), (10, 20), (32, 25)]:
        table = [random.randint(0, 2**n - 1) for _ in range(table_size)]
        op = TableLookup(table)
        re_symbolic = _re_symbolic_lookup(op)
        re_numeric = lambda assgn: _re_numeric_lookup(op, assgn)
        verify_re(re_symbolic, re_numeric, {"n": n})
