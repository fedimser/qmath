from typing import Protocol

from psiqworkbench import QUInt


class Multiplier(Protocol):
    """Interfeace for quantum integer multiplier: `c:=a*b`.

    Multiplier computes product of 2 quantum unsigned integers `a`, `b` and
    stores the result in a register `c` (which must be prepared in zero state).
    """

    def _compute(self, a: QUInt, b: QUInt, c: QUInt) -> None:
        pass
