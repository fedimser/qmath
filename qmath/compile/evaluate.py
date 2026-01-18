import ast

from psiqworkbench import QPU, QUInt, QFixed, Qubrick
from psiqworkbench.filter_presets import BIT_DEFAULT

from qmath.utils.symbolic import alloc_temp_qreg_like
from qmath.func.common import MultiplyAdd, Add, AddConst

# Type alias to represent quantum register or a literal number.
QValue = QFixed | float


# Ensures that x is of type QValue.
def _make_qvalue(x) -> QValue:
    if isinstance(x, QFixed):
        return x
    if isinstance(x, int) or isinstance(x, float):
        return float(x)
    raise ValueError("Unsupported type", type(x))


ops = []


class EvaluateExpression(Qubrick):
    """Evaluates arithmetic expression."""

    def __init__(self, expr: str, **kwargs):
        super().__init__(**kwargs)
        self.expr = expr
        self.vars = dict()

    def _implement_unary_op(self, op: ast.BinOp, arg: QValue) -> QValue:
        print("UNARY OP:", op, arg)
        raise ValueError(f"Unsupported unary op: {op}.")

    def _implement_binary_op(self, op: ast.BinOp, arg1: QValue, arg2: QValue) -> QValue:
        if isinstance(op, ast.Add):
            return self._add(arg1, arg2)
        if isinstance(op, ast.Mult):
            return self._mul(arg1, arg2)
        raise ValueError(f"Unsupported binary op: {op}.")

    def _add(self, arg1: QValue, arg2: QValue) -> QValue:
        if isinstance(arg1, float) and isinstance(arg2, float):
            return arg1 + arg2
        if isinstance(arg1, float):
            return self._add(arg2, arg1)

        assert isinstance(arg1, QFixed)
        # TODO: check if we are allowed to mutate or not.
        if isinstance(arg2, QFixed):
            Add().compute(arg1, arg2)
            return arg1
        else:
            assert isinstance(arg2, float)
            AddConst(arg2).compute(arg1)
            return arg1

    def _mul(self, arg1: QValue, arg2: QValue) -> QValue:
        if isinstance(arg1, float) and isinstance(arg2, float):
            return arg1 * arg2
        if isinstance(arg1, float):
            return self._mul(arg2, arg1)

        assert isinstance(arg1, QFixed)
        assert isinstance(arg2, QFixed)
        _, ans = alloc_temp_qreg_like(self, arg1)
        MultiplyAdd().compute(ans, arg1, arg2)
        return ans

    def _convert_ast_node(self, node) -> QFixed | float:
        if isinstance(node, ast.BinOp):
            arg1 = self._convert_ast_node(node.left)
            arg2 = self._convert_ast_node(node.right)
            return self._implement_binary_op(node.op, arg1, arg2)
        elif isinstance(node, ast.UnaryOp):
            arg = self._convert_ast_node(node.operand)
            return self._implement_unary_op(node.op, arg)
        elif isinstance(node, ast.Name):
            assert node.id in self.vars
            return self.vars[node.id]
        elif isinstance(node, ast.Constant):
            return _make_qvalue(node.value)
        else:
            raise ValueError(f"Cannot handle: {node}")

    def _compute(self, args: dict):
        self.vars = dict()
        for key, value in args.items():
            self.vars[key] = _make_qvalue(value)

        root = ast.parse(self.expr, mode="eval")
        ans = self._convert_ast_node(root.body)
        self.set_result_qreg(ans)
