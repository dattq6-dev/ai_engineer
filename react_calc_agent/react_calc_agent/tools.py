"""
LAYER 5 — TOOL
==============
Tool = (JSON Schema mô tả cho model)  +  (hàm Python thực thi deterministic).

Model KHÔNG chạy code. Model chỉ sinh ra một content block:
    {"type": "tool_use", "id": "toolu_...", "name": "calculator", "input": {...}}
Chúng ta đọc block đó, chạy hàm Python thật, rồi trả về:
    {"type": "tool_result", "tool_use_id": "toolu_...", "content": "...", "is_error": false}

Nguồn contract:
  https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
  https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls

CẢNH BÁO BẢO MẬT (quan trọng với hệ thống ngân hàng):
  TUYỆT ĐỐI không dùng `eval()` / `exec()` cho biểu thức do LLM sinh ra.
  Ở đây dùng AST allow-list: chỉ những node toán học được phép tồn tại.
  `eval("__import__('os').system('rm -rf /')")` là RCE thật sự, không phải giả định.
"""

from __future__ import annotations

import ast
import math
import operator
import statistics as _stats
from dataclasses import dataclass
from typing import Any, Callable

# ======================================================================
# 1. SAFE EXPRESSION EVALUATOR (AST allow-list)
# ======================================================================

_BIN_OPS: dict[type, Callable[[Any, Any], Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPS: dict[type, Callable[[Any], Any]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

# Chỉ các hàm thuần tuý, không I/O, không side-effect.
_FUNCS: dict[str, Callable[..., Any]] = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": lambda *a: sum(a[0]) if len(a) == 1 and isinstance(a[0], (list, tuple)) else sum(a),
    "sqrt": math.sqrt,
    "log": math.log,      # log(x) = ln(x); log(x, base)
    "log10": math.log10,
    "log2": math.log2,
    "exp": math.exp,
    "floor": math.floor,
    "ceil": math.ceil,
    "factorial": math.factorial,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "atan": math.atan,
    "degrees": math.degrees,
    "radians": math.radians,
    "hypot": math.hypot,
}

_CONSTS: dict[str, float] = {"pi": math.pi, "e": math.e, "tau": math.tau}

# Chặn DoS: 2**10**9 sẽ treo máy.
_MAX_EXPR_LEN = 500
_MAX_POW_EXPONENT = 1024
_MAX_FACTORIAL = 170


class CalculationError(Exception):
    """Lỗi có thể trả về cho model để nó tự sửa (recoverable)."""


def safe_eval(expression: str) -> float | int:
    """Đánh giá biểu thức số học một cách an toàn bằng AST allow-list."""
    expr = expression.strip()
    if not expr:
        raise CalculationError("Biểu thức rỗng.")
    if len(expr) > _MAX_EXPR_LEN:
        raise CalculationError(f"Biểu thức quá dài (>{_MAX_EXPR_LEN} ký tự).")
    # Người dùng VN hay viết 1.000.000 hoặc dùng dấu × ÷ −
    expr = expr.replace("×", "*").replace("÷", "/").replace("−", "-").replace("^", "**")

    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:  # noqa: BLE001
        raise CalculationError(f"Sai cú pháp: {exc.msg}") from exc

    return _eval_node(tree.body)


def _eval_node(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        raise CalculationError(f"Hằng số không được phép: {node.value!r}")

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _BIN_OPS:
            raise CalculationError(f"Toán tử không được phép: {op_type.__name__}")
        left, right = _eval_node(node.left), _eval_node(node.right)
        if op_type is ast.Pow and abs(_as_number(right)) > _MAX_POW_EXPONENT:
            raise CalculationError(f"Số mũ quá lớn (>{_MAX_POW_EXPONENT}).")
        try:
            return _BIN_OPS[op_type](left, right)
        except ZeroDivisionError as exc:
            raise CalculationError("Chia cho 0.") from exc
        except OverflowError as exc:
            raise CalculationError("Tràn số (overflow).") from exc

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _UNARY_OPS:
            raise CalculationError(f"Toán tử đơn không được phép: {op_type.__name__}")
        return _UNARY_OPS[op_type](_eval_node(node.operand))

    if isinstance(node, ast.Name):
        if node.id in _CONSTS:
            return _CONSTS[node.id]
        raise CalculationError(f"Tên không xác định: {node.id!r}")

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in _FUNCS:
            raise CalculationError("Chỉ được gọi các hàm toán học trong allow-list.")
        if node.keywords:
            raise CalculationError("Không hỗ trợ keyword argument.")
        fname = node.func.id
        args = [_eval_node(a) for a in node.args]
        if fname == "factorial" and (args and _as_number(args[0]) > _MAX_FACTORIAL):
            raise CalculationError(f"factorial() chỉ hỗ trợ n <= {_MAX_FACTORIAL}.")
        try:
            return _FUNCS[fname](*args)
        except (ValueError, TypeError, OverflowError) as exc:
            raise CalculationError(f"{fname}(): {exc}") from exc

    if isinstance(node, (ast.List, ast.Tuple)):
        return [_eval_node(e) for e in node.elts]

    raise CalculationError(f"Cú pháp không được phép: {type(node).__name__}")


def _as_number(v: Any) -> float:
    if isinstance(v, (int, float)):
        return float(v)
    raise CalculationError("Cần một số.")


def _fmt(value: Any, precision: int = 10) -> str:
    """Định dạng kết quả gọn, không mất thông tin."""
    if isinstance(value, list):
        return "[" + ", ".join(_fmt(v, precision) for v in value) + "]"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            raise CalculationError("Kết quả không hữu hạn (NaN/Inf).")
        if value == int(value) and abs(value) < 1e15:
            return str(int(value))
        return f"{round(value, precision):.{precision}f}".rstrip("0").rstrip(".")
    return str(value)


# ======================================================================
# 2. TOOL ABSTRACTION
# ======================================================================


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict[str, Any]
    fn: Callable[..., str]

    def to_api_spec(self) -> dict[str, Any]:
        """Đúng 3 field mà Messages API yêu cầu."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


class ToolRegistry:
    def __init__(self, tools: list[Tool] | None = None) -> None:
        self._tools: dict[str, Tool] = {}
        for t in tools or []:
            self.register(t)

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool trùng tên: {tool.name}")
        self._tools[tool.name] = tool

    def __contains__(self, name: object) -> bool:
        return name in self._tools

    def __len__(self) -> int:
        return len(self._tools)

    @property
    def names(self) -> list[str]:
        return list(self._tools)

    def api_specs(self) -> list[dict[str, Any]]:
        return [t.to_api_spec() for t in self._tools.values()]

    def invoke(self, name: str, tool_input: dict[str, Any]) -> tuple[str, bool]:
        """Trả về (content, is_error). KHÔNG bao giờ raise ra ngoài.

        Lý do: lỗi tool phải quay lại model dưới dạng tool_result với
        is_error=true để model tự sửa, chứ không làm sập cả run.
        """
        tool = self._tools.get(name)
        if tool is None:
            return (f"ToolNotFound: '{name}'. Công cụ hợp lệ: {self.names}", True)
        try:
            return (tool.fn(**tool_input), False)
        except CalculationError as exc:
            return (f"CalculationError: {exc}", True)
        except TypeError as exc:
            return (f"InvalidArguments: {exc}", True)
        except Exception as exc:  # noqa: BLE001 - biên phòng thủ cuối cùng
            return (f"{type(exc).__name__}: {exc}", True)


# ======================================================================
# 3. CÁC TOOL CỤ THỂ
# ======================================================================


def _calculator(expression: str, precision: int = 10) -> str:
    value = safe_eval(expression)
    return f"{expression.strip()} = {_fmt(value, precision)}"


calculator = Tool(
    name="calculator",
    description=(
        "Đánh giá CHÍNH XÁC một biểu thức số học bằng máy tính deterministic. "
        "BẮT BUỘC dùng cho mọi phép cộng/trừ/nhân/chia, luỹ thừa, căn, log, phần trăm, "
        "làm tròn — kể cả khi phép tính trông có vẻ dễ. "
        "Toán tử: + - * / // % ** (hoặc ^). "
        "Hàm: abs round min max sum sqrt log log10 log2 exp floor ceil factorial "
        "sin cos tan atan degrees radians hypot. Hằng: pi, e, tau. "
        "Ví dụ input: {'expression': '(1250000 * 0.085) / 12'}. "
        "Không hỗ trợ biến, gán, hay ký hiệu đại số — hãy thay số vào trước."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Biểu thức số học thuần tuý, đã thay hết số vào. VD: '365 * 24 * 3600'",
            },
            "precision": {
                "type": "integer",
                "description": "Số chữ số thập phân tối đa của kết quả (mặc định 10).",
                "minimum": 0,
                "maximum": 15,
            },
        },
        "required": ["expression"],
    },
    fn=_calculator,
)


def _loan_payment(principal: float, annual_rate_pct: float, months: int, method: str = "annuity") -> str:
    """Trả góp đều (annuity/EMI) hoặc giảm dần theo dư nợ gốc (reducing)."""
    if principal <= 0 or months <= 0:
        raise CalculationError("principal và months phải > 0.")
    if annual_rate_pct < 0:
        raise CalculationError("annual_rate_pct không được âm.")
    i = annual_rate_pct / 100.0 / 12.0

    if method == "annuity":
        if i == 0:
            pmt = principal / months
        else:
            pmt = principal * i * (1 + i) ** months / ((1 + i) ** months - 1)
        total = pmt * months
        return (
            f"method=annuity principal={_fmt(principal)} annual_rate_pct={_fmt(annual_rate_pct)} "
            f"months={months} monthly_rate={_fmt(i)} | "
            f"monthly_payment={_fmt(pmt, 2)} total_paid={_fmt(total, 2)} "
            f"total_interest={_fmt(total - principal, 2)}"
        )

    if method == "reducing":
        principal_part = principal / months
        first = principal_part + principal * i
        last = principal_part + principal_part * i
        total_interest = sum(
            (principal - principal_part * k) * i for k in range(months)
        )
        return (
            f"method=reducing principal={_fmt(principal)} annual_rate_pct={_fmt(annual_rate_pct)} "
            f"months={months} | principal_per_month={_fmt(principal_part, 2)} "
            f"first_payment={_fmt(first, 2)} last_payment={_fmt(last, 2)} "
            f"total_interest={_fmt(total_interest, 2)} "
            f"total_paid={_fmt(principal + total_interest, 2)}"
        )

    raise CalculationError("method phải là 'annuity' hoặc 'reducing'.")


loan_payment = Tool(
    name="loan_payment",
    description=(
        "Tính lịch trả nợ vay: tiền trả hàng tháng, tổng lãi, tổng phải trả. "
        "method='annuity' = trả góp đều mỗi tháng (EMI); "
        "method='reducing' = lãi tính trên dư nợ gốc giảm dần (phổ biến ở NHTM Việt Nam). "
        "Dùng tool này thay vì tự tính công thức annuity bằng calculator."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "principal": {"type": "number", "description": "Số tiền vay gốc."},
            "annual_rate_pct": {"type": "number", "description": "Lãi suất NĂM tính theo %, VD 8.5 nghĩa là 8.5%/năm."},
            "months": {"type": "integer", "description": "Số kỳ trả (tháng).", "minimum": 1},
            "method": {"type": "string", "enum": ["annuity", "reducing"], "description": "Phương pháp tính."},
        },
        "required": ["principal", "annual_rate_pct", "months"],
    },
    fn=_loan_payment,
)


def _descriptive_stats(numbers: list[float]) -> str:
    if not numbers:
        raise CalculationError("Danh sách rỗng.")
    nums = [float(n) for n in numbers]
    out = {
        "n": len(nums),
        "sum": sum(nums),
        "mean": _stats.fmean(nums),
        "median": _stats.median(nums),
        "min": min(nums),
        "max": max(nums),
    }
    if len(nums) >= 2:
        out["stdev_sample"] = _stats.stdev(nums)
        out["variance_sample"] = _stats.variance(nums)
    return " ".join(f"{k}={_fmt(v, 6)}" for k, v in out.items())


descriptive_stats = Tool(
    name="descriptive_stats",
    description=(
        "Thống kê mô tả trên một dãy số: n, tổng, trung bình, trung vị, min, max, "
        "độ lệch chuẩn mẫu, phương sai mẫu. Dùng khi người dùng đưa một danh sách số "
        "và hỏi trung bình/tổng/độ lệch chuẩn."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "numbers": {
                "type": "array",
                "items": {"type": "number"},
                "description": "Dãy số cần thống kê.",
                "minItems": 1,
            }
        },
        "required": ["numbers"],
    },
    fn=_descriptive_stats,
)


def default_registry() -> ToolRegistry:
    return ToolRegistry([calculator, loan_payment, descriptive_stats])
