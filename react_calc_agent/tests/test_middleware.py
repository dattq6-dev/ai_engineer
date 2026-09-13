"""Test LỚP MIDDLEWARE — nhận diện intent, ép tool_choice, chống bịa số, chặn tool."""

from decimal import Decimal

import pytest

from react_calc_agent.middleware import (
    MathIntentRouter,
    NumberGroundingGuard,
    ToolGuard,
    extract_numbers,
    normalize_number,
)
from react_calc_agent.model import ModelRequest, text_response, tool_use_response
from react_calc_agent.state import AgentState, ToolCall
from react_calc_agent.tools import default_registry

# ======================================================================
# 1. Chuẩn hoá số — nền tảng của guard
# ======================================================================


@pytest.mark.parametrize(
    "token,expected",
    [
        ("1234", "1234"),
        ("1.234", "1234"),          # kiểu VN: phân cách nghìn
        ("1,234", "1234"),          # kiểu EN: phân cách nghìn
        ("1.234.567", "1234567"),
        ("1,234,567", "1234567"),
        ("8.5", "8.5"),
        ("8,5", "8.5"),             # kiểu VN: phân cách thập phân
        ("1.234,56", "1234.56"),
        ("1,234.56", "1234.56"),
        ("-3", "-3"),
        ("1e3", "1E+3"),
    ],
)
def test_normalize_number(token, expected):
    assert normalize_number(token) == Decimal(expected)


def test_trailing_punctuation_does_not_break_extraction():
    """Regression: "... là 408." từng bị nuốt cả dấu chấm cuối câu vào token,
    khiến số bị bỏ qua và guard im lặng cho qua số bịa."""
    assert extract_numbers("Kết quả là 408.") == [Decimal("408")]
    assert extract_numbers("Khoảng 9.449.772.000.000.") == [Decimal("9449772000000")]
    assert extract_numbers("Giá 1.250.000đ, phí 50.000đ.") == [Decimal("1250000"), Decimal("50000")]


def test_list_markers_are_not_data():
    """'1. Bước một' — số 1 là đánh số danh sách, không phải dữ liệu."""
    text = "1. Bước đầu\n2. Bước hai\nKết quả là 408"
    assert extract_numbers(text) == [Decimal("408")]


# ======================================================================
# 2. MathIntentRouter — nhận diện request tính toán
# ======================================================================


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Tính giúp tôi 17 * 24", "math"),
        ("1234567 nhân 7654321 bằng bao nhiêu?", "math"),
        ("What is 45.7 divided by 3.2?", "math"),
        ("Khoản vay 1.250.000.000 lãi suất 9,6%/năm trong 240 tháng trả góp bao nhiêu mỗi tháng?", "math"),
        ("Trung bình của 12, 15, 19, 22 là bao nhiêu?", "math"),
        ("ReAct agent là gì?", "non_math"),
        ("Giải thích khái niệm lãi kép", "non_math"),
        ("Chào bạn", "non_math"),
        ("Viết giúp tôi một email cảm ơn khách hàng", "non_math"),
    ],
)
def test_intent_classification(text, expected):
    intent, _ = MathIntentRouter.classify(text)
    assert intent == expected, f"{text!r} -> {intent}"


def test_conceptual_question_with_numbers_is_not_forced():
    """'Giải thích lãi suất 8% nghĩa là gì' — có số nhưng là câu hỏi khái niệm."""
    intent, evidence = MathIntentRouter.classify("Giải thích lãi suất 8% nghĩa là gì?")
    assert intent in {"math", "unknown", "non_math"}
    assert any("conceptual" in e for e in evidence)


def test_router_forces_tool_use_then_releases():
    router = MathIntentRouter()
    state = AgentState(user_input="Tính 17 * 24")
    router.before_agent(state)
    assert state.intent == "math"

    req = ModelRequest(system="", messages=[], tools=[])
    # Bước 1: chưa có observation -> BẮT BUỘC gọi tool
    assert router.before_model(state, req).tool_choice == {"type": "any"}

    # Sau khi đã có observation -> nhả ra "auto" để model được kết luận
    state.tool_calls.append(
        ToolCall(id="t1", name="calculator", input={"expression": "17*24"}, step=1, output="17*24 = 408")
    )
    assert router.before_model(state, req).tool_choice == {"type": "auto"}


def test_router_does_not_force_on_non_math():
    router = MathIntentRouter()
    state = AgentState(user_input="ReAct agent là gì?")
    router.before_agent(state)
    req = ModelRequest(system="", messages=[], tools=[])
    assert router.before_model(state, req).tool_choice == {"type": "auto"}


def test_no_infinite_force_loop():
    """Nếu ép 'any' mãi mãi, agent không bao giờ kết luận được -> phải nhả."""
    router = MathIntentRouter()
    state = AgentState(user_input="Tính 2+2")
    router.before_agent(state)
    state.tool_calls.append(
        ToolCall(id="t", name="calculator", input={"expression": "2+2"}, step=1, output="2+2 = 4")
    )
    req = router.before_model(state, ModelRequest(system="", messages=[], tools=[]))
    assert req.tool_choice["type"] == "auto"


# ======================================================================
# 3. NumberGroundingGuard — chống bịa số
# ======================================================================


def _state_with_tool(expr: str, out: str, user_input: str) -> AgentState:
    guard = NumberGroundingGuard()
    state = AgentState(user_input=user_input)
    guard.before_agent(state)
    call = ToolCall(id="t1", name="calculator", input={"expression": expr}, step=1, output=out)
    guard.after_tool(state, call)
    state.tool_calls.append(call)
    return state


def test_guard_accepts_number_from_tool_output():
    guard = NumberGroundingGuard()
    state = _state_with_tool("17*24", "17*24 = 408", "Tính 17 * 24")
    state.intent = "math"
    guard.after_model(state, text_response("Kết quả là 408."))
    assert state.retry_requested is False
    assert state.warnings == []


def test_guard_rejects_hallucinated_number():
    guard = NumberGroundingGuard()
    state = _state_with_tool("17*24", "17*24 = 408", "Tính 17 * 24")
    state.intent = "math"
    guard.after_model(state, text_response("Kết quả là 418."))  # sai + chưa qua tool
    assert state.retry_requested is True
    assert "418" in state.scratch["pending_correction"]


def test_guard_accepts_rounded_presentation():
    """Tool trả 104166.6666667, câu trả lời viết 104166.67 -> vẫn hợp lệ."""
    guard = NumberGroundingGuard()
    state = _state_with_tool(
        "(1250000*0.1)/12", "(1250000*0.1)/12 = 10416.6666666667", "Tính (1250000*0.1)/12"
    )
    state.intent = "math"
    guard.after_model(state, text_response("Khoảng 10416.67 mỗi tháng."))
    assert state.retry_requested is False


def test_guard_does_not_block_tool_use_turn():
    """Guard chỉ chạy ở lượt KẾT LUẬN, không chặn lượt đang gọi tool."""
    guard = NumberGroundingGuard()
    state = AgentState(user_input="Tính 2+2")
    state.intent = "math"
    guard.after_model(state, tool_use_response("calculator", {"expression": "2+2"}))
    assert state.retry_requested is False


def test_guard_fails_open_after_max_retries():
    guard = NumberGroundingGuard()
    state = _state_with_tool("17*24", "17*24 = 408", "Tính 17 * 24")
    state.intent = "math"
    state.retries_used = state.max_retries
    guard.after_model(state, text_response("Kết quả là 999."))
    assert state.retry_requested is False          # không chặn nữa
    assert state.warnings and "999" in state.warnings[0]   # nhưng để lại vết


def test_guard_strict_mode_fails_closed():
    guard = NumberGroundingGuard(strict=True)
    state = _state_with_tool("17*24", "17*24 = 408", "Tính 17 * 24")
    state.intent = "math"
    state.retries_used = state.max_retries
    guard.after_model(state, text_response("Kết quả là 999."))
    assert state.status == "failed"


def test_guard_skips_non_math_answers():
    guard = NumberGroundingGuard()
    state = AgentState(user_input="ReAct là gì?")
    state.intent = "non_math"
    guard.before_agent(state)
    guard.after_model(state, text_response("ReAct ra đời năm 2022 theo bài báo arXiv 2210.03629."))
    assert state.retry_requested is False


# ======================================================================
# 4. ToolGuard
# ======================================================================


def test_tool_guard_blocks_unknown_tool():
    guard = ToolGuard(default_registry())
    state = AgentState(user_input="x")
    call = guard.before_tool(state, ToolCall(id="1", name="rm_rf", input={}, step=1))
    assert call.blocked_reason and "không tồn tại" in call.blocked_reason


def test_tool_guard_blocks_missing_required_arg():
    guard = ToolGuard(default_registry())
    state = AgentState(user_input="x")
    call = guard.before_tool(state, ToolCall(id="1", name="calculator", input={}, step=1))
    assert call.blocked_reason and "Thiếu tham số" in call.blocked_reason


def test_tool_guard_blocks_unknown_arg():
    guard = ToolGuard(default_registry())
    state = AgentState(user_input="x")
    call = guard.before_tool(
        state, ToolCall(id="1", name="calculator", input={"expression": "1+1", "shell": "sh"}, step=1)
    )
    assert call.blocked_reason and "không hợp lệ" in call.blocked_reason


def test_tool_guard_blocks_duplicate_call():
    guard = ToolGuard(default_registry())
    state = AgentState(user_input="x")
    state.tool_calls.append(
        ToolCall(id="1", name="calculator", input={"expression": "2+2"}, step=1, output="2+2 = 4")
    )
    call = guard.before_tool(
        state, ToolCall(id="2", name="calculator", input={"expression": "2+2"}, step=2)
    )
    assert call.blocked_reason and "Đã gọi y hệt" in call.blocked_reason


def test_tool_guard_enforces_budget():
    guard = ToolGuard(default_registry(), max_calls=2)
    state = AgentState(user_input="x")
    for k in range(2):
        state.tool_calls.append(
            ToolCall(id=str(k), name="calculator", input={"expression": f"{k}+1"}, step=1, output="ok")
        )
    call = guard.before_tool(
        state, ToolCall(id="9", name="calculator", input={"expression": "9+9"}, step=3)
    )
    assert call.blocked_reason and "hạn mức" in call.blocked_reason
