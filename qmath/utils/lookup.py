import math
from typing import Optional

from psiqworkbench import QFixed, Qubits, QUInt, SymbolicQubits
from psiqworkbench.qubricks import Qubrick
from psiqworkbench.symbolics.qubrick_costs import QubrickCosts

from .gates import write_uint


class TableLookup(Qubrick):
    """Assigns target ⊕= table[input].

    Reference: https://arxiv.org/pdf/1805.03662 (fig. 7).
    """

    def __init__(self, table: list[int], **kwargs):
        super().__init__(**kwargs)
        assert len(table) >= 2
        self.table = table
        self.address_size = int(math.ceil(math.log2(len(table))))

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

    def _compute(self, address: QUInt, target: QUInt):
        m = self.address_size
        assert address.num_qubits == m, f"Address size must be exactly {m}."
        address[m - 1].x()
        address_rec = address[0 : m - 1] if m > 1 else None
        self._lookup_ctrl(address[m - 1], address_rec, target, self.table[0 : 2 ** (m - 1)])
        address[m - 1].x()
        self._lookup_ctrl(address[m - 1], address_rec, target, self.table[2 ** (m - 1) :])

    def _compute_elbows(self):
        """Computes number of left/right elbows for given table size.

        num_elbows≈ts and abs(num_elbows-ts)<log2(ts), where ts=len(table).
        However, there is no exact closed formula. To get exact value, we have
        to simulate the construction.

        g(m, ts) - Number of elbows placed by call to _lookup_ctrl,
        where m=len(address), ts=len(table).
        """

        def g(m, ts):
            if ts == 0 or m == 0:
                return 0
            half = 2 ** (m - 1)
            return 1 + g(m - 1, min(ts, half)) + g(m - 1, max(0, ts - half))

        return g(self.address_size, len(self.table)) - 1

    def _estimate(self, address: SymbolicQubits, target: SymbolicQubits):
        # Cost of TableLookup is fully determined by the table.
        num_elbows = self._compute_elbows()
        bits_sum = sum(v.bit_count() for v in self.table)

        cost = QubrickCosts(
            gidney_lelbows=num_elbows,
            gidney_relbows=num_elbows,
            local_ancillae=self.address_size - 1,
            active_volume=53 * num_elbows + 4 * bits_sum,
        )
        self.get_qc().add_cost_event(cost)
