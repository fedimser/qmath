"""Bitwise functions."""

from psiqworkbench import QFixed, QInt, QUInt, Qubits
from psiqworkbench.qubricks import Qubrick


class HighestSetBit(Qubrick):
    """Finds most significant set bit in a and sets it in ans."""

    def _compute(self, a: Qubits, ans: Qubits):
        flag: Qubits = self.alloc_temp_qreg(1, "flag")

        # For each input qubit i compute which output qubit must be set if i is MSB.
        for i in range(a.num_qubits - 1, -1, -1):
            # Copy a[i] to ans[j], but only if flag is unset.
            flag.x()
            ans[i].lelbow(a[i] | flag)
            flag.x()

            # If ans[i]=1 (which implies flag was unset), set the flag.
            # All less significant qubits will be ignored.
            flag.x(ans[i])
