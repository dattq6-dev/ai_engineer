"""
LAYER 3 — MIDDLEWARE
====================
Middleware là các "vòng bọc" (onion) quanh mỗi lượt gọi model và mỗi lần gọi tool.
Chúng biến agent từ một vòng while thành một hệ thống có thể kiểm soát được.

Vòng đời hook:

    before_agent   (theo thứ tự khai báo)
    ┌── vòng lặp ReAct, mỗi bước: ───────────────────────────────┐
    │   before_model  (thuận)   -> được sửa ModelRequest         │
    │        [gọi model]                                         │
    │   after_model   (nghịch)  -> được sửa ModelResponse        │
    │   before_tool   (thuận)   -> được chặn/sửa ToolCall        │
    │        [chạy tool]                                         │
    │   after_tool    (nghịch)  -> được sửa observation          │
    └────────────────────────────────────────────────────────────┘
    after_agent    (nghịch)

`before_*` chạy xuôi, `after_*` chạy ngược — giống middleware HTTP. Nhờ vậy
middleware khai báo đầu tiên là lớp ngoài cùng, bọc tất cả các lớp bên trong.

Đối chiếu LangChain v1: tương đương `before_model` / `wrap_model_call` /
`after_model` trong tham số `middleware=[...]` của `create_agent`.
"""

from __future__ import annotations

import re
import time
from decimal import Decimal, InvalidOperation
from typing import Any

from .model import ModelRequest, ModelResponse
from .prompt import RETRY_UNGROUNDED_NUMBER
from .state import AgentState, ToolCall

# ======================================================================
# Base
# ======================================================================


class Middleware:
    """Kế thừa và override hook bạn cần. Hook mặc định là no-op."""

    name: str = "middleware"

    def before_agent(self, state: AgentState) -> None: ...

    def before_model(self, state: AgentState, request: ModelRequest) -> ModelRequest:
        return request

    def after_model(self, state: AgentState, response: ModelResponse) -> ModelResponse:
        return response

    def before_tool(self, state: AgentState, call: ToolCall) -> ToolCall:
        return call

    def after_tool(self, state: AgentState, call: ToolCall) -> ToolCall:
        return call

    def after_agent(self, state: AgentState) -> None: ...


# ======================================================================
# 1. Trích xuất & so khớp số  (dùng chung cho router + guard)
# ======================================================================

# Bắt token số: 1.234.567,89 | 1,234,567.89 | 8.5 | 8,5 | 1200 | -3
# Lưu ý `(?:[\d.,]*\d)?`: token BẮT BUỘC kết thúc bằng chữ số, nếu không thì dấu
# chấm cuối câu ("... là 408.") sẽ bị nuốt vào token và phá vỡ bộ chuẩn hoá.
# Lookahead dùng `(?![\d])` chứ không phải `(?![\w])`: tiền tệ kiểu Việt Nam viết
# dính đuôi ("1.250.000đ", "50.000 VND") sẽ làm regex backtrack và cắt cụt số.
_NUMBER_TOKEN = re.compile(r"(?<![\w.,])[-+]?\d(?:[\d.,]*\d)?(?:[eE][-+]?\d+)?(?![\d])")
# Bỏ ký hiệu đánh số danh sách ở đầu dòng ("1. ", "2) ") để không bị coi là dữ liệu.
_LIST_MARKER = re.compile(r"(?m)^\s{0,6}\d{1,2}[.)]\s")


def normalize_number(token: str) -> Decimal | None:
    """Chuẩn hoá token số về Decimal, xử lý cả dấu phân cách kiểu VN và EN.

    Quy tắc: dấu phân cách XUẤT HIỆN CUỐI CÙNG là dấu thập phân, TRỪ KHI nó
    chia phần đuôi thành đúng nhóm 3 chữ số (khi đó là phân cách nghìn).
        "1.234.567"  -> 1234567      "1,5"      -> 1.5
        "1,234.56"   -> 1234.56      "1.234,56" -> 1234.56
    """
    tok = token.strip().replace(" ", "").rstrip(".,")   # bỏ dấu câu bám đuôi
    if not tok or not any(ch.isdigit() for ch in tok):
        return None

    sign = ""
    if tok[0] in "+-":
        sign, tok = ("-" if tok[0] == "-" else ""), tok[1:]

    exp = ""
    if "e" in tok.lower():
        idx = tok.lower().index("e")
        tok, exp = tok[:idx], tok[idx:]

    has_dot, has_comma = "." in tok, "," in tok
    if has_dot and has_comma:
        dec_sep = "." if tok.rindex(".") > tok.rindex(",") else ","
        thou_sep = "," if dec_sep == "." else "."
        tok = tok.replace(thou_sep, "").replace(dec_sep, ".")
    elif has_dot or has_comma:
        sep = "." if has_dot else ","
        head, _, tail = tok.rpartition(sep)
        if len(tail) == 3 and tok.count(sep) >= 1 and head and head.replace(sep, "").isdigit():
            # 1.234 / 1,234 / 1.234.567 -> phân cách nghìn
            tok = tok.replace(sep, "")
        else:
            tok = tok.replace(sep, ".")
    try:
        return Decimal(sign + tok + exp)
    except InvalidOperation:
        return None


def extract_numbers(text: str, strip_list_markers: bool = True) -> list[Decimal]:
    if strip_list_markers:
        text = _LIST_MARKER.sub("", text)
    out: list[Decimal] = []
    for m in _NUMBER_TOKEN.finditer(text):
        val = normalize_number(m.group())
        if val is not None:
            out.append(val)
    return out


def _is_grounded(value: Decimal, verified: set[str], max_round_digits: int = 6) -> bool:
    """Một số được coi là "có cơ sở" nếu nó bằng, hoặc là bản làm tròn, của
    một số đã xuất hiện trong đề bài / input tool / output tool."""
    for raw in verified:
        try:
            ref = Decimal(raw)
        except InvalidOperation:
            continue
        if ref == value:
            return True
        for d in range(max_round_digits + 1):
            q = Decimal(1).scaleb(-d)
            try:
                if ref.quantize(q) == value.quantize(q):
                    return True
            except (InvalidOperation, ValueError):
                continue
    return False


# ======================================================================
# 2. MathIntentRouter — "nhận diện request có phải tính toán không"
# ======================================================================

_ARITH_EXPR = re.compile(r"\d\s*(?:[-+*/^%]|\*\*|×|÷)\s*[-+(]?\s*\d")

_MATH_KEYWORDS_VI = {
    "tính", "tinh toan", "tính toán", "bằng bao nhiêu", "bao nhiêu", "tổng", "hiệu",
    "tích", "thương", "cộng", "trừ", "nhân", "chia", "phần trăm", "trung bình",
    "trung vị", "độ lệch chuẩn", "phương sai", "lãi", "lãi suất", "gốc", "kỳ hạn",
    "trả góp", "khoản vay", "chênh lệch", "căn bậc", "luỹ thừa", "lũy thừa",
    "giai thừa", "tỷ lệ", "tỉ lệ", "quy đổi", "làm tròn", "mỗi tháng",
}
_MATH_KEYWORDS_EN = {
    "calculate", "compute", "how much", "how many", "sum of", "total", "average",
    "mean", "median", "stdev", "standard deviation", "variance", "percent", "%",
    "interest", "installment", "loan", "payment", "sqrt", "square root", "factorial",
    "divided by", "multiplied by", "times", "round to",
}
# Dấu hiệu câu hỏi khái niệm — chống dương tính giả ("giải thích lãi kép là gì")
_CONCEPTUAL = {
    "là gì", "nghĩa là", "giải thích", "khái niệm", "định nghĩa", "tại sao", "vì sao",
    "so sánh khái niệm", "what is", "explain", "definition", "why is", "difference between",
}


class MathIntentRouter(Middleware):
    """Phân loại ý định và biến kết quả thành RÀNG BUỘC CỨNG qua `tool_choice`.

    Đây là câu trả lời kỹ thuật cho yêu cầu "agent phải nhận diện request tính toán
    để không trả lời ngẫu nhiên":
      * intent = math + đề có số  -> tool_choice = {"type": "any"}  (BẮT BUỘC gọi tool)
      * đã có observation         -> tool_choice = {"type": "auto"} (nhường quyền kết luận)
      * intent != math            -> tool_choice = {"type": "auto"}

    Chọn "any" thay vì "tool" cụ thể để model vẫn được chọn đúng công cụ
    (calculator / loan_payment / descriptive_stats) trong nhóm.
    Nguồn tool_choice: https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
    """

    name = "math_intent_router"

    def __init__(self, force_tool_on_math: bool = True) -> None:
        self.force_tool_on_math = force_tool_on_math

    # --- phân loại ---
    @staticmethod
    def classify(text: str) -> tuple[str, list[str]]:
        low = text.lower()
        evidence: list[str] = []

        numbers = extract_numbers(low, strip_list_markers=False)
        if _ARITH_EXPR.search(low):
            evidence.append("arithmetic_expression")
        kw = [k for k in (_MATH_KEYWORDS_VI | _MATH_KEYWORDS_EN) if k in low]
        if kw:
            evidence.append(f"keywords={sorted(kw)[:5]}")
        if len(numbers) >= 2:
            evidence.append(f"numbers={len(numbers)}")
        conceptual = [c for c in _CONCEPTUAL if c in low]
        if conceptual:
            evidence.append(f"conceptual={conceptual[:3]}")

        # Luật quyết định, xếp theo độ mạnh của bằng chứng.
        if "arithmetic_expression" in evidence and not conceptual:
            return "math", evidence
        if kw and numbers and not (conceptual and not kw):
            return "math", evidence
        if conceptual and not numbers:
            return "non_math", evidence
        if kw and not numbers:
            return "unknown", evidence          # VD: "tính lãi suất thế nào?" -> để model tự quyết
        if numbers and not kw and not conceptual:
            return "unknown", evidence
        return "non_math", evidence

    # --- hook ---
    def before_agent(self, state: AgentState) -> None:
        intent, evidence = self.classify(state.user_input)
        state.intent = intent  # type: ignore[assignment]
        state.intent_evidence = evidence
        state.scratch["input_number_count"] = len(extract_numbers(state.user_input, False))
        state.log("intent_classified", intent=intent, evidence=evidence)

    def before_model(self, state: AgentState, request: ModelRequest) -> ModelRequest:
        has_observation = any(c.executed and not c.is_error for c in state.tool_calls)
        must_force = (
            self.force_tool_on_math
            and state.intent == "math"
            and state.scratch.get("input_number_count", 0) >= 1
            and not has_observation
        )
        request.tool_choice = {"type": "any"} if must_force else {"type": "auto"}
        state.log("tool_choice_set", tool_choice=request.tool_choice, forced=must_force)
        return request


# ======================================================================
# 3. NumberGroundingGuard — chống "bịa số"
# ======================================================================


class NumberGroundingGuard(Middleware):
    """Kiểm chứng sau khi model kết luận: mọi con số trong câu trả lời cuối
    phải truy vết được về (a) đề bài, (b) tham số đưa vào tool, hoặc (c) output tool.

    Nếu không truy vết được -> tiêm một user message sửa lỗi và bắt agent chạy lại.
    Hết hạn mức retry -> không chặn nữa nhưng ghi `state.warnings` để audit.

    ĐÁNH ĐỔI (phải biết rõ khi đưa lên production):
      Guard này có thể báo dương tính giả khi model trình bày lại số dưới dạng
      dẫn xuất (VD tool trả 0.0070833 nhưng câu trả lời viết "0,71%/tháng").
      Vì vậy nó được thiết kế "fail-open sau N lần": ưu tiên không chặn oan,
      nhưng luôn để lại vết cảnh báo. Muốn chặt hơn thì đặt strict=True.
    """

    name = "number_grounding_guard"

    def __init__(self, strict: bool = False, allow_small_ints_up_to: int = 0) -> None:
        self.strict = strict
        self.allow_small_ints_up_to = allow_small_ints_up_to

    def before_agent(self, state: AgentState) -> None:
        for n in extract_numbers(state.user_input, strip_list_markers=False):
            state.verified_numbers.add(str(n))

    def after_tool(self, state: AgentState, call: ToolCall) -> ToolCall:
        # Cả input lẫn output đều là "đã kiểm chứng": input do người dùng/model
        # đưa vào và đã hiển thị ra để đối chiếu; output do máy tính sinh ra.
        for blob in (str(call.input), call.output or ""):
            for n in extract_numbers(blob, strip_list_markers=False):
                state.verified_numbers.add(str(n))
        return call

    def after_model(self, state: AgentState, response: ModelResponse) -> ModelResponse:
        if response.wants_tool:
            return response  # chưa phải câu trả lời cuối
        if state.intent == "non_math" and not state.tool_calls:
            return response  # câu hỏi khái niệm: không áp guard số

        answer = response.text()
        ungrounded = [
            n
            for n in extract_numbers(answer)
            if not (n == n.to_integral_value() and abs(n) <= self.allow_small_ints_up_to)
            and not _is_grounded(n, state.verified_numbers)
        ]
        if not ungrounded:
            return response

        if state.retries_used >= state.max_retries:
            msg = f"Số chưa kiểm chứng được sau {state.retries_used} lần thử: {ungrounded}"
            state.warnings.append(msg)
            state.log("grounding_failed_open", numbers=[str(n) for n in ungrounded])
            if self.strict:
                state.status = "failed"
                state.final_answer = (
                    "Không thể xác thực các con số trong câu trả lời. Đã dừng để tránh đưa số sai. "
                    f"Chi tiết: {msg}"
                )
            return response

        state.retries_used += 1
        state.retry_requested = True
        state.log("grounding_retry", numbers=[str(n) for n in ungrounded], attempt=state.retries_used)
        state.scratch["pending_correction"] = RETRY_UNGROUNDED_NUMBER.format(
            numbers=", ".join(str(n) for n in ungrounded)
        )
        return response


# ======================================================================
# 4. ToolGuard — kiểm soát đầu vào công cụ
# ======================================================================


class ToolGuard(Middleware):
    """Chặn trước khi thực thi: tool lạ, thiếu tham số bắt buộc, gọi lặp vô ích,
    vượt hạn mức số lần gọi. Ở ngân hàng, lớp này là nơi bạn nhét thêm
    kiểm tra hạn mức, PII, và whitelist nghiệp vụ."""

    name = "tool_guard"

    def __init__(self, registry: Any, max_calls: int = 12, block_duplicates: bool = True) -> None:
        self.registry = registry
        self.max_calls = max_calls
        self.block_duplicates = block_duplicates

    def before_tool(self, state: AgentState, call: ToolCall) -> ToolCall:
        if call.name not in self.registry:
            call.blocked_reason = f"Tool '{call.name}' không tồn tại. Hợp lệ: {self.registry.names}"
            return call

        executed = [c for c in state.tool_calls if c.executed]
        if len(executed) >= self.max_calls:
            call.blocked_reason = f"Vượt hạn mức {self.max_calls} lần gọi công cụ trong một run."
            return call

        spec = next(t for t in self.registry.api_specs() if t["name"] == call.name)
        missing = [k for k in spec["input_schema"].get("required", []) if k not in call.input]
        if missing:
            call.blocked_reason = f"Thiếu tham số bắt buộc: {missing}"
            return call

        unknown = [k for k in call.input if k not in spec["input_schema"].get("properties", {})]
        if unknown:
            call.blocked_reason = f"Tham số không hợp lệ: {unknown}"
            return call

        if self.block_duplicates:
            for prev in executed:
                if prev.name == call.name and prev.input == call.input and not prev.is_error:
                    call.blocked_reason = (
                        f"Đã gọi y hệt ở bước {prev.step}, kết quả: {prev.output}. "
                        "Dùng lại kết quả đó, đừng gọi lại."
                    )
                    return call
        return call


# ======================================================================
# 5. Tracing — quan sát được thì mới vận hành được
# ======================================================================


class TracingMiddleware(Middleware):
    name = "tracing"

    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose
        self._t0 = 0.0

    def _p(self, msg: str) -> None:
        if self.verbose:
            print(msg, flush=True)

    def before_agent(self, state: AgentState) -> None:
        self._p(
            f"\n=== RUN {state.run_id} ===\nUSER: {state.user_input}\n"
            f"intent={state.intent}  evidence={state.intent_evidence}"
        )

    def before_model(self, state: AgentState, request: ModelRequest) -> ModelRequest:
        self._t0 = time.time()
        self._p(f"\n[bước {state.step}] THINK -> model (tool_choice={request.tool_choice['type']})")
        return request

    def after_model(self, state: AgentState, response: ModelResponse) -> ModelResponse:
        dt = (time.time() - self._t0) * 1000
        txt = response.text()
        if txt:
            self._p(f"  thought: {txt[:300]}")
        for tu in response.tool_uses():
            self._p(f"  ACT: {tu['name']}({tu['input']})")
        self._p(f"  stop_reason={response.stop_reason} ({dt:.0f} ms)")
        return response

    def after_tool(self, state: AgentState, call: ToolCall) -> ToolCall:
        tag = "ERR " if call.is_error else "OBS "
        self._p(f"  {tag}{call.name} -> {call.output}")
        return call

    def after_agent(self, state: AgentState) -> None:
        self._p(
            f"\n=== KẾT THÚC status={state.status} steps={state.step} "
            f"tools={len(state.tool_calls)} retries={state.retries_used} "
            f"tokens={state.usage.as_dict()['total_tokens']} ==="
        )
        if state.warnings:
            self._p(f"CẢNH BÁO: {state.warnings}")


def default_middleware(registry: Any, verbose: bool = False) -> list[Middleware]:
    """THỨ TỰ CÓ Ý NGHĨA — và đây là chỗ rất dễ sai.

    `before_*` chạy xuôi, `after_*` chạy ngược. Tracing phải đứng **cuối** để:
      * before_model: nó chạy SAU MathIntentRouter -> nhìn thấy `tool_choice` THẬT
        sẽ được gửi lên API, chứ không phải giá trị mặc định.
      * after_model / after_agent: nó chạy ĐẦU trong chuỗi ngược -> nhìn thấy
        response NGUYÊN BẢN của model trước khi guard can thiệp.

    Đặt Tracing lên đầu list là một lỗi thật đã xảy ra khi viết dự án này: trace in ra
    `tool_choice=auto` trong khi request gửi đi là `any`. Log sai còn tệ hơn không log,
    vì nó khiến bạn đi điều tra nhầm hướng.
    """
    return [
        MathIntentRouter(),
        ToolGuard(registry),
        NumberGroundingGuard(),
        TracingMiddleware(verbose=verbose),
    ]
