# ReAct Calculator Agent

Agent ReAct viết bằng **Anthropic SDK thuần** (tự cầm vòng lặp tool-use, không dùng
LangChain/LangGraph), gồm đủ 5 lớp: **prompt · model · middleware · state · tool**.

Mục tiêu: **mọi con số trong câu trả lời phải đến từ một phép tính tất định, không
phải từ suy luận xác suất của LLM.**

---

## Cài đặt & chạy

```bash
pip install -r requirements.txt

# 1. Xem bộ phân loại intent hoạt động (KHÔNG cần API key)
python -m react_calc_agent.run --demo

# 2. Chạy toàn bộ test offline (88 test, ~0.1 giây, KHÔNG cần API key)
pytest

# 3. Chạy agent thật
export ANTHROPIC_API_KEY=sk-ant-...
python -m react_calc_agent.run "1234567 nhân 7654321 bằng bao nhiêu?"
python -m react_calc_agent.run --repl

# 4. Reality check với model thật
pytest tests/test_live_smoke.py -v -s

# 5. Benchmark: có công cụ vs để model tự nhẩm
python bench/accuracy_bench.py
```

Đổi model: `export CALCAGENT_MODEL=claude-opus-5` (mặc định `claude-sonnet-5`).

---

## Kiến trúc 5 lớp

```
                      ┌──────────── PROMPT ─────────────┐
                      │ prompt.py                       │
                      │ Hiến pháp: "không được tính nhẩm"│
                      └────────────────┬────────────────┘
                                       │ system=
┌─────────── STATE ──────────┐         ▼         ┌────────── TOOL ──────────┐
│ state.py                   │   ┌───────────┐   │ tools.py                 │
│ messages, step, intent,    │◄─►│  agent.py │◄─►│ calculator (AST an toàn) │
│ verified_numbers, usage,   │   │  vòng lặp │   │ loan_payment             │
│ tool_calls, trace          │   │   ReAct   │   │ descriptive_stats        │
└────────────────────────────┘   └─────┬─────┘   └──────────────────────────┘
                                       │ tools=, tool_choice=
┌──────── MIDDLEWARE ────────┐         ▼         ┌───────── MODEL ──────────┐
│ middleware.py              │                   │ model.py                 │
│ MathIntentRouter  ← nhận diện request tính toán│ AnthropicModel (SDK thật)│
│ ToolGuard                  │                   │ FakeModel (test offline) │
│ NumberGroundingGuard ← chống bịa số            │ ModelRequest/Response    │
│ Tracing (đứng cuối, xem §)  │                  └──────────────────────────┘
└────────────────────────────┘
```

## Vòng lặp ReAct

```
USER: "1234567 nhân 7654321 bằng bao nhiêu?"
  │
  ├─ before_agent → MathIntentRouter: intent = "math"  (keywords + 2 số)
  │
  ├─ BƯỚC 1 ─ before_model → tool_choice = {"type": "any"}   ★ ÉP PHẢI GỌI TOOL
  │            model → THOUGHT + tool_use{calculator, "1234567 * 7654321"}
  │            before_tool → ToolGuard: OK
  │            chạy tool  → OBSERVATION "1234567 * 7654321 = 9449772114007"
  │            after_tool → verified_numbers += {9449772114007, ...}
  │
  ├─ BƯỚC 2 ─ before_model → tool_choice = {"type": "auto"}  ★ NHẢ RA ĐỂ KẾT LUẬN
  │            model → "Kết quả là 9.449.772.114.007."
  │            after_model → NumberGroundingGuard: mọi số đều truy vết được → PASS
  │
  └─ final_answer
```

## Ba lớp phòng thủ chống "trả lời ngẫu nhiên"

| # | Lớp | Loại ràng buộc | Cài ở đâu | Thất bại thì sao |
|---|-----|----------------|-----------|------------------|
| 1 | System prompt cấm tính nhẩm | **Mềm** (model vẫn có thể vi phạm) | `prompt.py` | Lớp 2 bắt |
| 2 | `tool_choice={"type":"any"}` khi intent = math | **Cứng** (API bảo đảm) | `MathIntentRouter` | Lớp 3 bắt |
| 3 | Kiểm chứng số sau khi trả lời | **Hậu kiểm** (retry / cảnh báo) | `NumberGroundingGuard` | Ghi `state.warnings` để audit |

Chỉ có lớp prompt là "mong model ngoan". Lớp 2 và 3 là bảo đảm kỹ thuật.

## Cấu trúc file

```
react_calc_agent/
├── prompt.py        LỚP 1 — system prompt + thông điệp sửa lỗi
├── model.py         LỚP 2 — AnthropicModel / FakeModel / ModelRequest / ModelResponse
├── middleware.py    LỚP 3 — MathIntentRouter, ToolGuard, NumberGroundingGuard, Tracing
├── state.py         LỚP 4 — AgentState, ToolCall, Usage
├── tools.py         LỚP 5 — safe_eval (AST allow-list) + 3 công cụ
├── agent.py         Orchestrator — vòng lặp ReAct
└── run.py           CLI
tests/
├── test_tools.py        độ chính xác + chống RCE/DoS
├── test_middleware.py   intent, tool_choice, grounding, guard
├── test_agent_loop.py   end-to-end với FakeModel
└── test_live_smoke.py   reality check với API thật (tự skip nếu thiếu key)
bench/accuracy_bench.py  có công cụ vs tự nhẩm
docs/ARCHITECTURE.md     giải thích kiến trúc & thiết kế
docs/GIAI-THICH.md       tài liệu học: từng khái niệm + 3 câu hỏi kiểm tra
```

## Mở rộng

Thêm công cụ — 1 chỗ duy nhất:

```python
from react_calc_agent.tools import Tool, default_registry

fx = Tool(
    name="fx_convert",
    description="Quy đổi ngoại tệ theo tỷ giá cho trước. Dùng khi câu hỏi có 2 loại tiền tệ.",
    input_schema={
        "type": "object",
        "properties": {
            "amount": {"type": "number"},
            "rate": {"type": "number", "description": "Tỷ giá 1 đơn vị nguồn = ? đơn vị đích"},
        },
        "required": ["amount", "rate"],
    },
    fn=lambda amount, rate: f"{amount} * {rate} = {amount * rate}",
)
registry = default_registry()
registry.register(fx)
```

Thêm middleware — kế thừa `Middleware`, override hook cần dùng, chèn vào list.
`before_*` chạy xuôi, `after_*` chạy ngược (mô hình onion). **Thứ tự quan trọng**:
`TracingMiddleware` phải đứng cuối để `before_model` của nó nhìn thấy `tool_choice`
thật sau khi `MathIntentRouter` đã sửa — xem docstring của `default_middleware()`.

## Nguồn tham chiếu

- Yao et al., *ReAct: Synergizing Reasoning and Acting in Language Models*, ICLR 2023 — <https://arxiv.org/abs/2210.03629>
- Anthropic — *Tool use overview* — <https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview>
- Anthropic — *Handle tool calls* — <https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls>
- Anthropic — *Model IDs and versioning* — <https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions>
