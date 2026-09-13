"""Test VÒNG LẶP ReAct end-to-end bằng FakeModel — tất định, không tốn token."""

import pytest

from react_calc_agent.agent import ReActAgent
from react_calc_agent.middleware import default_middleware
from react_calc_agent.model import FakeModel, ModelResponse, text_response, tool_use_response
from react_calc_agent.state import Usage
from react_calc_agent.tools import default_registry


def make_agent(model, **kw):
    reg = default_registry()
    return ReActAgent(model=model, tools=reg, middleware=default_middleware(reg), **kw)


def test_tracing_sees_the_real_tool_choice():
    """Regression: Tracing từng đứng đầu list nên `before_model` của nó chạy TRƯỚC
    MathIntentRouter và log ra `auto` trong khi request thật gửi `any`."""
    from react_calc_agent.middleware import TracingMiddleware

    mws = default_middleware(default_registry())
    assert isinstance(mws[-1], TracingMiddleware), "Tracing phải đứng cuối chuỗi before_*"

    model = FakeModel(
        script=[tool_use_response("calculator", {"expression": "17 * 24"}), text_response("408.")]
    )
    seen: list[str] = []
    trace = mws[-1]
    original = trace.before_model

    def spy(state, request):
        seen.append(request.tool_choice["type"])
        return original(state, request)

    trace.before_model = spy  # type: ignore[method-assign]
    ReActAgent(model=model, tools=default_registry(), middleware=mws).run("Tính 17 * 24")
    assert seen == ["any", "auto"] == [c.tool_choice["type"] for c in model.calls]


# ======================================================================
# Đường đi hạnh phúc: THINK -> ACT -> OBSERVE -> ANSWER
# ======================================================================


def test_full_react_cycle():
    model = FakeModel(
        script=[
            tool_use_response("calculator", {"expression": "17 * 24"}, text="Cần tính 17*24."),
            text_response("17 × 24 = 408."),
        ]
    )
    state = make_agent(model).run("Tính giúp tôi 17 * 24")

    assert state.status == "succeeded"
    assert state.step == 2
    assert state.final_answer == "17 × 24 = 408."
    assert [c.name for c in state.tool_calls] == ["calculator"]
    assert state.tool_calls[0].output == "17 * 24 = 408"
    assert state.usage.as_dict()["total_tokens"] == 40


def test_message_transcript_shape_matches_api_contract():
    """Kiểm tra đúng hình dạng messages mà Messages API yêu cầu."""
    model = FakeModel(
        script=[
            tool_use_response("calculator", {"expression": "2+2"}, tool_id="toolu_abc"),
            text_response("Bằng 4."),
        ]
    )
    state = make_agent(model).run("Tính 2+2")
    msgs = state.messages

    assert [m["role"] for m in msgs] == ["user", "assistant", "user", "assistant"]
    # observation là USER message chứa tool_result (không phải role 'tool')
    obs = msgs[2]["content"][0]
    assert obs["type"] == "tool_result"
    assert obs["tool_use_id"] == "toolu_abc"      # phải khớp id của tool_use
    assert "is_error" not in obs


def test_tool_choice_sequence_is_any_then_auto():
    model = FakeModel(
        script=[
            tool_use_response("calculator", {"expression": "17 * 24"}),
            text_response("408."),
        ]
    )
    make_agent(model).run("Tính 17 * 24")
    assert [c.tool_choice["type"] for c in model.calls] == ["any", "auto"]


def test_non_math_question_uses_no_tool():
    model = FakeModel(script=[text_response("ReAct là mô hình đan xen suy luận và hành động.")])
    state = make_agent(model).run("ReAct agent là gì?")

    assert state.intent == "non_math"
    assert state.tool_calls == []
    assert model.calls[0].tool_choice == {"type": "auto"}
    assert state.status == "succeeded"


# ======================================================================
# Nhiều tool trong một lượt (parallel tool use)
# ======================================================================


def test_parallel_tool_use_each_gets_a_result():
    resp = ModelResponse(
        content=[
            {"type": "tool_use", "id": "a", "name": "calculator", "input": {"expression": "2+2"}},
            {"type": "tool_use", "id": "b", "name": "calculator", "input": {"expression": "3*3"}},
        ],
        stop_reason="tool_use",
        usage=Usage(5, 5),
    )
    model = FakeModel(script=[resp, text_response("4 và 9.")])
    state = make_agent(model).run("Tính 2+2 và 3*3")

    results = state.messages[2]["content"]
    assert [r["tool_use_id"] for r in results] == ["a", "b"]
    assert len(state.tool_calls) == 2


# ======================================================================
# Lỗi tool phải quay lại model, không làm sập run
# ======================================================================


def test_tool_error_is_fed_back_and_recovered():
    model = FakeModel(
        script=[
            tool_use_response("calculator", {"expression": "1/0"}, tool_id="t1"),
            tool_use_response("calculator", {"expression": "1/0.5"}, tool_id="t2"),
            text_response("Không chia được cho 0; 1/0.5 = 2."),
        ]
    )
    state = make_agent(model).run("Tính 1 / 0 rồi 1 / 0.5")

    err_block = state.messages[2]["content"][0]
    assert err_block["is_error"] is True
    assert "Chia cho 0" in err_block["content"]
    assert state.status == "succeeded"


def test_blocked_tool_returns_error_block_not_crash():
    model = FakeModel(
        script=[
            tool_use_response("shell", {"cmd": "rm -rf /"}, tool_id="bad"),
            text_response("Tôi không có công cụ đó."),
        ]
    )
    state = make_agent(model).run("Tính 1 + 1")
    assert state.tool_calls[0].is_error is True
    assert "Blocked" in state.tool_calls[0].output
    assert state.status == "succeeded"


# ======================================================================
# Guard chống bịa số trong vòng lặp thật
# ======================================================================


def test_hallucinated_number_triggers_retry_and_is_corrected():
    model = FakeModel(
        script=[
            tool_use_response("calculator", {"expression": "1234567 * 7654321"}),
            text_response("Kết quả khoảng 9.449.772.000.000."),   # BỊA
            text_response("Kết quả chính xác là 9449772114007."),  # đúng theo tool
        ]
    )
    state = make_agent(model).run("1234567 nhân 7654321 bằng bao nhiêu?")

    assert state.retries_used == 1
    assert state.status == "succeeded"
    assert "9449772114007" in state.final_answer
    # thông điệp sửa lỗi đã được tiêm vào transcript
    assert any(
        m["role"] == "user"
        and m["content"][0].get("type") == "text"
        and "KIỂM SOÁT HỆ THỐNG" in m["content"][0]["text"]
        for m in state.messages
    )


def test_persistent_hallucination_fails_open_with_warning():
    bad = text_response("Kết quả là 9.449.772.000.000.")
    model = FakeModel(
        script=[tool_use_response("calculator", {"expression": "1234567 * 7654321"}), bad, bad, bad]
    )
    state = make_agent(model).run("1234567 nhân 7654321 bằng bao nhiêu?")

    assert state.retries_used == 2
    assert state.warnings, "phải để lại cảnh báo để audit"
    assert state.status == "succeeded"


# ======================================================================
# Ngân sách & an toàn vòng lặp
# ======================================================================


def test_step_budget_halts_infinite_loop():
    """Model 'bướng' luôn gọi tool -> agent phải tự dừng, không treo."""
    model = FakeModel(
        handler=lambda req, n: tool_use_response(
            "calculator", {"expression": f"{n} + 1"}, tool_id=f"t{n}"
        )
    )
    state = make_agent(model, max_steps=4).run("Tính 1+1")

    assert state.status == "halted"
    assert state.step == 4
    assert len(model.calls) == 4


def test_model_exception_is_contained():
    class Boom:
        def invoke(self, request):
            raise RuntimeError("429 rate limit")

    state = make_agent(Boom()).run("Tính 2+2")
    assert state.status == "failed"
    assert "429" in state.final_answer


def test_summary_is_auditable():
    model = FakeModel(
        script=[tool_use_response("calculator", {"expression": "17 * 24"}), text_response("408.")]
    )
    summary = make_agent(model).run("Tính 17 * 24").summary()

    for key in ("run_id", "status", "intent", "steps", "tool_calls", "usage", "final_answer"):
        assert key in summary
    assert summary["tool_calls"][0]["output"] == "17 * 24 = 408"


# ======================================================================
# Tính tất định: cùng input -> cùng đường đi
# ======================================================================


def test_deterministic_across_runs():
    def build():
        return FakeModel(
            script=[tool_use_response("calculator", {"expression": "17 * 24"}), text_response("408.")]
        )

    a = make_agent(build()).run("Tính 17 * 24")
    b = make_agent(build()).run("Tính 17 * 24")
    assert a.final_answer == b.final_answer
    assert [c.input for c in a.tool_calls] == [c.input for c in b.tool_calls]
