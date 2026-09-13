"""
REALITY CHECK — test với model THẬT.

Các test trong file này tự SKIP nếu không có ANTHROPIC_API_KEY, nên `pytest tests`
vẫn chạy sạch trên CI không có secret.

Chạy:
    export ANTHROPIC_API_KEY=sk-ant-...
    pytest tests/test_live_smoke.py -v -s

Mục đích: chứng minh những giả định về contract API là ĐÚNG TRÊN THỰC TẾ,
chứ không chỉ đúng với FakeModel:
  1. tool_choice={"type":"any"} thực sự ép model gọi công cụ.
  2. stop_reason thực sự trả về "tool_use".
  3. Agent tính đúng phép nhân lớn mà model tự nhẩm hay sai.
  4. Câu hỏi khái niệm không bị gọi công cụ vô cớ.
"""

import os

import pytest

from react_calc_agent import ReActAgent, default_registry
from react_calc_agent.model import AnthropicModel, ModelRequest

pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"), reason="Cần ANTHROPIC_API_KEY để chạy test thật"
)

MODEL_ID = os.getenv("CALCAGENT_MODEL", "claude-sonnet-5")

# Phép nhân 7 chữ số: đây là vùng mà LLM tự nhẩm gần như luôn sai vài chữ số giữa.
BIG_A, BIG_B = 1234567, 7654321
BIG_EXPECT = str(BIG_A * BIG_B)  # 9449772114007


@pytest.fixture(scope="module")
def agent():
    return ReActAgent(model=AnthropicModel(model=MODEL_ID), verbose=True)


def test_tool_choice_any_really_forces_a_tool_call():
    """Kiểm chứng trực tiếp contract của API, không qua agent."""
    model = AnthropicModel(model=MODEL_ID)
    resp = model.invoke(
        ModelRequest(
            system="Bạn là trợ lý.",
            messages=[{"role": "user", "content": [{"type": "text", "text": "Xin chào, bạn khỏe không?"}]}],
            tools=default_registry().api_specs(),
            tool_choice={"type": "any"},
            max_tokens=512,
        )
    )
    assert resp.stop_reason == "tool_use"
    assert resp.tool_uses(), "tool_choice='any' phải ép sinh ra tool_use block"


def test_big_multiplication_is_exact(agent):
    state = agent.run(f"{BIG_A} nhân {BIG_B} bằng bao nhiêu?")
    assert state.intent == "math"
    assert state.tool_calls, "phải gọi công cụ"
    assert BIG_EXPECT in "".join(c.output or "" for c in state.tool_calls)
    digits = state.final_answer.replace(".", "").replace(",", "").replace(" ", "")
    assert BIG_EXPECT in digits, f"Câu trả lời sai: {state.final_answer}"


def test_banking_loan_question(agent):
    state = agent.run(
        "Khách vay 1.250.000.000 VND, lãi suất 9,6%/năm, kỳ hạn 240 tháng, "
        "trả góp đều. Mỗi tháng trả bao nhiêu và tổng lãi là bao nhiêu?"
    )
    assert state.intent == "math"
    assert any(c.name in {"loan_payment", "calculator"} for c in state.tool_calls)
    assert state.status == "succeeded"
    assert not state.warnings, f"guard cảnh báo số chưa kiểm chứng: {state.warnings}"


def test_multi_step_reasoning(agent):
    state = agent.run(
        "Một chi nhánh có 3 phòng với 17, 23 và 31 nhân viên. "
        "Nếu mỗi nhân viên xử lý 48 hồ sơ/tháng thì cả chi nhánh xử lý bao nhiêu hồ sơ trong 1 quý?"
    )
    assert "10224" in state.final_answer.replace(".", "").replace(",", "")


def test_conceptual_question_does_not_call_tools(agent):
    state = agent.run("ReAct agent khác gì so với một chatbot thông thường? Giải thích ngắn gọn.")
    assert state.intent == "non_math"
    assert state.tool_calls == [], f"gọi tool vô cớ: {state.tool_calls}"


def test_missing_data_triggers_clarification_not_invention(agent):
    """Thiếu lãi suất -> agent phải HỎI LẠI, không được tự bịa ra con số."""
    state = ReActAgent(model=AnthropicModel(model=MODEL_ID)).run(
        "Tôi vay 500 triệu trong 5 năm thì tổng lãi phải trả là bao nhiêu?"
    )
    low = (state.final_answer or "").lower()
    assert any(k in low for k in ("lãi suất", "chưa", "cần", "bao nhiêu", "cung cấp")), state.final_answer
