from typing import Optional

from psiqworkbench import QFixed, Qubits, QUInt
from psiqworkbench.qubricks import Qubrick

from .gates import write_uint


class TableLookup(Qubrick):
    """Assigns target ⊕= table[input].

    Reference: https://arxiv.org/pdf/1805.03662 (fig. 7).
    """

    def _lookup_ctrl(self, ctrl: Qubits, address: Optional[Qubits], target: QUInt, table: list[int]):
        if len(table) == 0:
            return
        if address is None:
            assert len(table) == 1
            write_uint(target, table[0], ctrl=ctrl)
            return

        m = len(address)
        assert len(table) <= 2**m

        anc = self.alloc_temp_qreg(1, "anc")
        address[m - 1].x()
        anc.lelbow(ctrl | address[m - 1])
        address[m - 1].x()
        address_rec = address[0 : m - 1] if m > 1 else None
        self._lookup_ctrl(anc, address_rec, target, table[0 : 2 ** (m - 1)])
        anc.x(ctrl)
        self._lookup_ctrl(anc, address_rec, target, table[2 ** (m - 1) :])
        anc.relbow(ctrl | address[m - 1])
        anc.release()

    def _compute(self, address: QUInt, target: QUInt, table: list[int]):
        m = len(address)
        assert 2 ** (m - 1) < len(table), "Address is too long."
        assert len(table) <= 2**m, "Table is too long."
        address[m - 1].x()
        address_rec = address[0 : m - 1] if m > 1 else None
        self._lookup_ctrl(address[m - 1], address_rec, target, table[0 : 2 ** (m - 1)])
        address[m - 1].x()
        self._lookup_ctrl(address[m - 1], address_rec, target, table[2 ** (m - 1) :])
