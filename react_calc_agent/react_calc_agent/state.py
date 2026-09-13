"""
LAYER 4 — STATE
===============
State là "bộ nhớ làm việc" của agent trong MỘT lần chạy (one run).

Nguyên tắc thiết kế quan trọng:
  * `messages` là state BẮT BUỘC vì Messages API của Anthropic là stateless —
    mỗi lần gọi API bạn phải gửi lại toàn bộ lịch sử hội thoại.
    (https://platform.claude.com/docs/en/api/messages)
  * Mọi thứ khác (step, intent, tool_calls, verified_numbers...) là state MỞ RỘNG
    do chúng ta tự định nghĩa — đây chính là chỗ mà middleware đọc/ghi để
    điều khiển hành vi agent.

So sánh với LangChain v1: đây là tương đương thủ công của `state_schema`.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Literal

Intent = Literal["math", "non_math", "unknown"]
Status = Literal["running", "succeeded", "halted", "failed"]


@dataclass
class Usage:
    """Kế toán token — ở ngân hàng thì đây là cost control, không phải option."""

    input_tokens: int = 0
    output_tokens: int = 0

    def add(self, other: "Usage") -> None:
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens

    def as_dict(self) -> dict[str, int]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens,
        }


@dataclass
class ToolCall:
    """Một lời gọi công cụ: từ lúc model đề xuất tới lúc có observation."""

    id: str                      # trùng với `id` của content block `tool_use`
    name: str
    input: dict[str, Any]
    step: int
    output: str | None = None
    is_error: bool = False
    blocked_reason: str | None = None
    latency_ms: float = 0.0

    @property
    def executed(self) -> bool:
        return self.output is not None


@dataclass
class AgentState:
    """Toàn bộ trạng thái của một run."""

    user_input: str
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    started_at: float = field(default_factory=time.time)

    # --- state lõi (bắt buộc cho Messages API) ---
    messages: list[dict[str, Any]] = field(default_factory=list)

    # --- state điều khiển vòng lặp ReAct ---
    step: int = 0
    max_steps: int = 8
    status: Status = "running"
    final_answer: str | None = None

    # --- state của intent router ---
    intent: Intent = "unknown"
    intent_evidence: list[str] = field(default_factory=list)

    # --- state của guardrail chống "bịa số" ---
    verified_numbers: set[str] = field(default_factory=set)
    retry_requested: bool = False
    retries_used: int = 0
    max_retries: int = 2
    warnings: list[str] = field(default_factory=list)

    # --- quan sát / audit ---
    tool_calls: list[ToolCall] = field(default_factory=list)
    trace: list[dict[str, Any]] = field(default_factory=list)
    usage: Usage = field(default_factory=Usage)

    # --- vùng nháp tự do cho middleware của bạn ---
    scratch: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Thao tác trên messages
    # ------------------------------------------------------------------
    def append_user_text(self, text: str) -> None:
        self.messages.append({"role": "user", "content": [{"type": "text", "text": text}]})

    def append_assistant_blocks(self, blocks: list[dict[str, Any]]) -> None:
        self.messages.append({"role": "assistant", "content": blocks})

    def append_tool_results(self, results: list[dict[str, Any]]) -> None:
        """tool_result LUÔN đi trong message có role='user'.

        Đây là điểm hay bị nhầm nhất khi tự viết vòng lặp ReAct:
        observation không phải role 'tool' như OpenAI, mà là user message
        chứa các block {"type": "tool_result", "tool_use_id": ...}.
        Nguồn: https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls
        """
        self.messages.append({"role": "user", "content": results})

    # ------------------------------------------------------------------
    # Quan sát
    # ------------------------------------------------------------------
    def log(self, event: str, **data: Any) -> None:
        self.trace.append(
            {
                "t": round(time.time() - self.started_at, 4),
                "step": self.step,
                "event": event,
                **data,
            }
        )

    def elapsed_ms(self) -> float:
        return (time.time() - self.started_at) * 1000

    def summary(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "intent": self.intent,
            "steps": self.step,
            "tool_calls": [
                {"name": c.name, "input": c.input, "output": c.output, "is_error": c.is_error}
                for c in self.tool_calls
            ],
            "retries_used": self.retries_used,
            "warnings": self.warnings,
            "usage": self.usage.as_dict(),
            "elapsed_ms": round(self.elapsed_ms(), 1),
            "final_answer": self.final_answer,
        }
