"""
ORCHESTRATOR — ráp 5 lớp thành vòng lặp ReAct
=============================================
ReAct = Reason + Act, đan xen suy luận và hành động trong cùng một vòng.
Nguồn gốc: Yao et al., "ReAct: Synergizing Reasoning and Acting in Language
Models", ICLR 2023 — arXiv:2210.03629 (https://arxiv.org/abs/2210.03629).

Vòng lặp thực thi:

    user_input
        │
        ├─ before_agent (middleware)            <- phân loại intent
        │
        ▼
    ┌───────────────── mỗi bước ─────────────────────────────────┐
    │  before_model  -> ép tool_choice                           │
    │  model.invoke  -> THOUGHT (+ ACTION)                       │
    │  after_model   -> guard kiểm chứng số                      │
    │                                                            │
    │  stop_reason == "tool_use" ?                               │
    │     CÓ   -> before_tool -> chạy tool -> after_tool          │
    │             -> OBSERVATION quay lại messages -> lặp tiếp    │
    │     KHÔNG-> đây là câu trả lời cuối -> thoát                │
    └────────────────────────────────────────────────────────────┘
        │
        └─ after_agent (middleware)
"""

from __future__ import annotations

import time
from typing import Any

from .middleware import Middleware, default_middleware
from .model import AnthropicModel, BaseModel, ModelRequest, ModelResponse
from .prompt import HALTED_NOTICE, build_system_prompt
from .state import AgentState, ToolCall
from .tools import ToolRegistry, default_registry


class ReActAgent:
    def __init__(
        self,
        model: BaseModel | None = None,
        tools: ToolRegistry | None = None,
        system_prompt: str | None = None,
        middleware: list[Middleware] | None = None,
        max_steps: int = 8,
        max_tokens: int = 2048,
        temperature: float = 0.0,
        verbose: bool = False,
    ) -> None:
        self.tools = tools or default_registry()
        self.model = model or AnthropicModel()
        self.system_prompt = system_prompt or build_system_prompt()
        self.middleware = middleware if middleware is not None else default_middleware(self.tools, verbose)
        self.max_steps = max_steps
        self.max_tokens = max_tokens
        self.temperature = temperature

    # ------------------------------------------------------------------
    def run(self, user_input: str) -> AgentState:
        state = AgentState(user_input=user_input, max_steps=self.max_steps)
        state.append_user_text(user_input)

        for mw in self.middleware:
            mw.before_agent(state)

        while state.step < state.max_steps:
            state.step += 1

            # ---------- THINK ----------
            request = ModelRequest(
                system=self.system_prompt,
                messages=state.messages,
                tools=self.tools.api_specs(),
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            for mw in self.middleware:
                request = mw.before_model(state, request)

            try:
                response = self.model.invoke(request)
            except Exception as exc:  # noqa: BLE001
                state.status = "failed"
                state.final_answer = f"Lỗi khi gọi model: {type(exc).__name__}: {exc}"
                state.log("model_error", error=str(exc))
                break

            state.usage.add(response.usage)
            for mw in reversed(self.middleware):
                response = mw.after_model(state, response)

            state.append_assistant_blocks(response.content)

            # ---------- guard yêu cầu làm lại ----------
            if state.retry_requested:
                state.retry_requested = False
                correction = state.scratch.pop("pending_correction", None)
                if correction:
                    state.append_user_text(correction)
                if state.status == "failed":
                    break
                continue

            # ---------- ACT + OBSERVE ----------
            tool_uses = response.tool_uses()
            if tool_uses:
                results = [self._execute(state, tu) for tu in tool_uses]
                state.append_tool_results(results)
                continue

            # ---------- KẾT LUẬN ----------
            state.final_answer = response.text()
            state.status = "succeeded"
            state.log("final_answer", chars=len(state.final_answer))
            break
        else:
            state.status = "halted"
            state.final_answer = HALTED_NOTICE.format(max_steps=state.max_steps)
            state.log("halted")

        for mw in reversed(self.middleware):
            mw.after_agent(state)
        return state

    # ------------------------------------------------------------------
    def _execute(self, state: AgentState, tool_use: dict[str, Any]) -> dict[str, Any]:
        """Chạy một tool_use và trả về đúng block tool_result tương ứng.

        BẤT BIẾN CỦA API: mỗi `tool_use.id` phải có đúng một `tool_result`
        với `tool_use_id` khớp, trong message user kế tiếp. Thiếu một cái là
        request sau sẽ bị từ chối.
        """
        call = ToolCall(
            id=tool_use["id"],
            name=tool_use["name"],
            input=dict(tool_use.get("input") or {}),
            step=state.step,
        )
        for mw in self.middleware:
            call = mw.before_tool(state, call)

        t0 = time.perf_counter()
        if call.blocked_reason:
            call.output, call.is_error = f"Blocked: {call.blocked_reason}", True
        else:
            call.output, call.is_error = self.tools.invoke(call.name, call.input)
        call.latency_ms = (time.perf_counter() - t0) * 1000

        for mw in reversed(self.middleware):
            call = mw.after_tool(state, call)

        state.tool_calls.append(call)
        state.log(
            "tool_executed",
            tool=call.name,
            input=call.input,
            output=call.output,
            is_error=call.is_error,
            latency_ms=round(call.latency_ms, 3),
        )
        block: dict[str, Any] = {
            "type": "tool_result",
            "tool_use_id": call.id,
            "content": call.output or "",
        }
        if call.is_error:
            block["is_error"] = True
        return block

    # ------------------------------------------------------------------
    def chat(self, user_input: str) -> str:
        """Tiện ích: chỉ lấy câu trả lời."""
        return self.run(user_input).final_answer or ""
