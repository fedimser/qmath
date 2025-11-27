from psiqworkbench import Qubits


class Qubit(Qubits):
    def __init__(self, q: Qubits):
        assert len(q) == 1
        super().__init__(q)

    @staticmethod
    def list(qs: Qubits) -> list["Qubit"]:
        return [Qubit(q) for q in qs]


def cnot(a: Qubit, b: Qubit):
    b.x(a)


def ccnot(a: Qubit, b: Qubit, c: Qubit):
    c.x(a | b)


def swap(a: Qubit, b: Qubit):
    a.swap(b)


def controlled_swap(ctrl: Qubit, a: Qubit, b: Qubit):
    ccnot(ctrl, a, b)
    ccnot(ctrl, b, a)
    ccnot(ctrl, a, b)


# Rotates qubits of P right by 1.
def rotate_right(p: list[Qubit]):
    k = len(p)
    k1 = k // 2
    for i in range(k1):
        swap(p[i], p[k - 1 - i])
    for i in range(k1 - 1 + (k % 2)):
        swap(p[i], p[k - 2 - i])
