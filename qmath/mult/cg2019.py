# Implementation of multiplier presented in paper:
#   Asymptotically Efficient Quantum Karatsuba Multiplication
#   Craig Gidney, 2019.
#   https://arxiv.org/abs/1904.07356
# All numbers are integer, Little Endian.
# Based off q# implementation from (https://github.com/fedimser/quant-arith-re/blob/main/lib/src/QuantumArithmetic/CG2019.qs)

from psiqworkbench import Qubits, QUInt, qubricks
from psiqworkbench.interoperability import implements
from psiqworkbench.qubricks import Qubrick, GidneyAdd

from ..utils.gates import ccnot, cnot

# from ..add.cdkm2004 import CDKMAdder

class schoolbook_multiplication(Qubrick):
    """
    Implementation of the schoolbook multiplication:
        "Asymptotically Efficient Quantum Karatsuba Multiplication",
        Craig Gidney, 2019.
        https://arxiv.org/abs/1904.07356
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "schoolbook multiplier"
        self.description = "Asymptotically efficient multiplier by Craig Gidney, 2019."
        self.gadder = qubricks.GidneyAdd()

    def _plusEqual(self, lvalue: Qubits, offset: Qubits):
        #trimmedOffset = offset[ : len(offset) - min([len(lvalue), len(offset)]) ] #Python doesnt include the last element -> could be a edian issue
        trimmedOffset = offset[ len(offset) - min([len(lvalue), len(offset)]) :] #to fix edian issue?
        pad_num_qubits = len(lvalue)-len(trimmedOffset)
        if len(trimmedOffset) > 0:
            pad = 0
            if pad_num_qubits > 0:
                pad: Qubits = self.alloc_temp_qreg(len(lvalue) - len(trimmedOffset), "pad")
            paddedOffset = trimmedOffset | pad #+ should be replaced with |
            self.gadder.compute(lvalue, paddedOffset) #use gidney adder (try making it work with this first)

    def _compute(self, a: Qubits, b: Qubits, c: Qubits): #parent class of all subtypes for Qubits vs QuInt?
        n1 = len(a)
        n2 = len(b)
        w: Qubits = self.alloc_temp_qreg(n2, "w")
        for k in range(n1):
            for i in range(n2):
                ccnot(b[i], a[k], w[i])
            #print(f"QUInt = {c.read()}")
            self._plusEqual(c[k: len(c) ], w)
            #print(f"QUInt = {c.read()}")
            for i in range(n2):
                ccnot(b[i], a[k], w[i])

class karatsub_multiplication(Qubrick):
    """
    Implementation of the multiplier presented in paper:
        "Asymptotically Efficient Quantum Karatsuba Multiplication",
        Craig Gidney, 2019.
        https://arxiv.org/abs/1904.07356
    """
    def __init__(self):
        super().__init__()
        self.name = "CG2019 Multiplier"
        self.description = "Asymptotically efficient multiplier by Craig Gidney, 2019."
        self.schoolbook_multiplier = schoolbook_multiplication()

    def _splitPadBuffer(self, buf: Qubits, pad: Qubits, basePieceSize: int, desiredPieceSize: int, pieceCount: int) -> list[Qubits]:
        """
        Splits buf into pieces of base_piece_size, pads each to desired_piece_size using pad.
        
        Args:
            buf: Buffer of qubits to split
            pad: Padding qubits (should have enough for all missing pieces)
            base_piece_size: Initial size of each piece from buf
            desired_piece_size: Target size after padding
            piece_count: Number of pieces to create
        
        Returns:
            List of Qubits objects, each of size desired_piece_size
        """
        result = [] #how to convert "mutable result : Qubit[][] = [];" from Q# to python?
        k_pad = 0

        for i in range(pieceCount):
            k_buf = i * basePieceSize
            res_i = []

            #extract from buffer if needed
            if(k_buf < len(buf)):
                res_i = buf[k_buf:min(k_buf + basePieceSize, len(buf))]
            
            #calculate how much padding is needed
            missing = desiredPieceSize - len(res_i)
            result += [res_i + pad[k_pad : k_pad + missing]]
            k_pad += missing

        return result
    
    def _mergeBufferRanges(work_registers: list[Qubits], start: int, length: int):
        result = [] #how to convert "mutable result : Qubit[] = [];" from Q# to python?
        for i in range(len(work_registers)):
            for j in range(length):
                result += [work_registers[i][start+j]]
        return result
    
    def _ceillg2(n:int) -> int:
        if (n <= 1):
            return 0
#        else:

    
#    def _compute(self, a: Qubits, b: Qubits, c: Qubits) -> None: