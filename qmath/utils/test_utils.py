from psiqworkbench import QPU, Qubits, QFixed
from psiqworkbench.ops.qpu_ops import convert_ops_to_cpp


class QPUTestHelper:
    def __init__(self, *, num_inputs=1, qubits_per_reg=20, radix=15, num_qubits=500):
        """A helper for QPU testing.

        Records compiled instructions to re-apply them later. This allows to
        compile circuit once and simulate it on different inputs.

        Designed for testing Qubricks that implement functions on QFixed
        registers of the same size and radix. Functions take one or more inputs
        and produce exactly one output.
        """
        self.num_inputs = num_inputs
        self.qubits_per_reg = qubits_per_reg
        self.radix = radix
        self.num_qubits = num_qubits

        self.qpu = QPU(filters=[">>64bit>>", ">>capture>>"])
        self.qpu.reset(self.num_qubits)
        self.inputs = self._create_inputs(self.qpu)
        self.prep_length = len(self.qpu.get_instructions())

    def _create_inputs(self, qpu):
        return [
            QFixed(
                self.qubits_per_reg,
                name=f"input_{i}",
                radix=self.radix,
                qpu=qpu,
            )
            for i in range(self.num_inputs)
        ]

    def record_op(self, result_qreg: QFixed) -> None:
        """Call this after applyting operation, passing output register.

        It will compile circuit for applied operations.
        """
        self.result_qreg_mask = result_qreg.mask()
        ops = self.qpu.get_instructions()[self.prep_length :]
        self.cpp_ops = convert_ops_to_cpp(ops)

    def apply_op(self, input_vals: list[float]) -> float:
        """Writes `input_vals` into inputs, applies compiled circuit and reads the result."""
        assert len(input_vals) == self.num_inputs
        qpu = QPU(filters=[">>64bit>>", ">>bit-sim>>"])
        sim = qpu.get_filter_by_name(">>bit-sim>>")

        qpu.reset(self.num_qubits)
        inputs = self._create_inputs(qpu)
        for i in range(self.num_inputs):
            inputs[i].write(input_vals[i])
        qpu.flush()

        sim._put_native(self.cpp_ops)
        result_qreg = QFixed(Qubits(from_mask=self.result_qreg_mask, name="temp", qpu=qpu), radix=self.radix)
        return result_qreg.read()
