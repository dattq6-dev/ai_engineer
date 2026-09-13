"""
LAYER 2 — MODEL
===============
Lớp mỏng bọc quanh Anthropic Messages API, với 2 mục tiêu:

  1. CHUẨN HOÁ: biến object của SDK thành dict thuần (`ModelResponse`) để
     phần còn lại của agent không phụ thuộc vào kiểu dữ liệu của SDK.
  2. THAY THẾ ĐƯỢC: `FakeModel` cài cùng interface -> test toàn bộ vòng lặp
     ReAct và middleware offline, không tốn token, không cần API key,
     và kết quả tất định (deterministic) nên CI không bị flaky.

Contract API dùng ở đây (đã đối chiếu tài liệu ngày 2026-09-12):
  - request:  model, max_tokens, system, messages, tools, tool_choice
  - response: .content (list block), .stop_reason, .usage
  - stop_reason == "tool_use" nghĩa là model đang yêu cầu gọi công cụ
  https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

from .state import Usage

# Model ID theo quy ước "dateless" từ thế hệ 4.6 trở đi: claude-{name}-{major}[-{minor}]
# https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions
DEFAULT_MODEL = os.getenv("CALCAGENT_MODEL", "claude-sonnet-5")


@dataclass
class ModelRequest:
    """Request đã chuẩn hoá — middleware được phép sửa object này trước khi gửi."""

    system: str
    messages: list[dict[str, Any]]
    tools: list[dict[str, Any]]
    tool_choice: dict[str, Any] = field(default_factory=lambda: {"type": "auto"})
    max_tokens: int = 2048
    temperature: float = 0.0
    model: str = DEFAULT_MODEL


@dataclass
class ModelResponse:
    """Response đã chuẩn hoá thành dict thuần."""

    content: list[dict[str, Any]]
    stop_reason: str
    usage: Usage = field(default_factory=Usage)
    raw: Any = None

    # -- tiện ích --
    def text(self) -> str:
        return "\n".join(b["text"] for b in self.content if b.get("type") == "text").strip()

    def tool_uses(self) -> list[dict[str, Any]]:
        return [b for b in self.content if b.get("type") == "tool_use"]

    @property
    def wants_tool(self) -> bool:
        return self.stop_reason == "tool_use" or bool(self.tool_uses())


class BaseModel(Protocol):
    """Interface tối thiểu mà agent cần. Bất cứ thứ gì cài đủ đây đều cắm được."""

    def invoke(self, request: ModelRequest) -> ModelResponse: ...


# ======================================================================
# Model thật
# ======================================================================


class AnthropicModel:
    def __init__(self, model: str = DEFAULT_MODEL, api_key: str | None = None, **client_kwargs: Any) -> None:
        try:
            import anthropic  # import trễ: tests offline không cần SDK
        except ImportError as exc:  # pragma: no cover
            raise ImportError("Cần cài SDK: pip install anthropic") from exc

        key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError(
                "Thiếu ANTHROPIC_API_KEY. Đặt biến môi trường hoặc truyền api_key=..."
            )
        self.model = model
        self._client = anthropic.Anthropic(api_key=key, **client_kwargs)

    def invoke(self, request: ModelRequest) -> ModelResponse:
        kwargs: dict[str, Any] = {
            "model": request.model or self.model,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "system": request.system,
            "messages": request.messages,
        }
        if request.tools:
            kwargs["tools"] = request.tools
            kwargs["tool_choice"] = request.tool_choice

        resp = self._client.messages.create(**kwargs)
        return ModelResponse(
            content=[_block_to_dict(b) for b in resp.content],
            stop_reason=resp.stop_reason or "end_turn",
            usage=Usage(
                input_tokens=getattr(resp.usage, "input_tokens", 0) or 0,
                output_tokens=getattr(resp.usage, "output_tokens", 0) or 0,
            ),
            raw=resp,
        )


def _block_to_dict(block: Any) -> dict[str, Any]:
    """Chuẩn hoá content block của SDK về dict thuần."""
    if isinstance(block, dict):
        return block
    btype = getattr(block, "type", None)
    if btype == "text":
        return {"type": "text", "text": block.text}
    if btype == "tool_use":
        return {
            "type": "tool_use",
            "id": block.id,
            "name": block.name,
            "input": dict(block.input or {}),
        }
    if btype == "thinking":
        # Khối thinking PHẢI được gửi lại nguyên vẹn kèm signature ở lượt sau.
        return {
            "type": "thinking",
            "thinking": getattr(block, "thinking", ""),
            "signature": getattr(block, "signature", ""),
        }
    if hasattr(block, "model_dump"):
        return block.model_dump()
    return {"type": str(btype)}


# ======================================================================
# Model giả — hạ tầng để test
# ======================================================================


class FakeModel:
    """Model tất định phục vụ test.

    Dùng một trong hai cách:
      * `FakeModel(script=[resp1, resp2, ...])` — phát lần lượt theo kịch bản.
      * `FakeModel(handler=lambda req, n: ModelResponse(...))` — logic động.
    """

    def __init__(
        self,
        script: list[ModelResponse] | None = None,
        handler: Callable[[ModelRequest, int], ModelResponse] | None = None,
    ) -> None:
        if not script and not handler:
            raise ValueError("Cần script hoặc handler.")
        self._script = list(script or [])
        self._handler = handler
        self.calls: list[ModelRequest] = []

    def invoke(self, request: ModelRequest) -> ModelResponse:
        # Lưu bản sao nông để test có thể kiểm tra tool_choice từng bước.
        self.calls.append(
            ModelRequest(
                system=request.system,
                messages=list(request.messages),
                tools=request.tools,
                tool_choice=dict(request.tool_choice),
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                model=request.model,
            )
        )
        n = len(self.calls) - 1
        if self._handler:
            return self._handler(request, n)
        if n >= len(self._script):
            raise AssertionError(f"FakeModel hết kịch bản ở lần gọi thứ {n + 1}.")
        return self._script[n]


# -- helper dựng response nhanh trong test --


def text_response(text: str, stop_reason: str = "end_turn") -> ModelResponse:
    return ModelResponse(
        content=[{"type": "text", "text": text}],
        stop_reason=stop_reason,
        usage=Usage(10, 10),
    )


def tool_use_response(
    name: str, tool_input: dict[str, Any], tool_id: str = "toolu_test_1", text: str | None = None
) -> ModelResponse:
    content: list[dict[str, Any]] = []
    if text:
        content.append({"type": "text", "text": text})
    content.append({"type": "tool_use", "id": tool_id, "name": name, "input": tool_input})
    return ModelResponse(content=content, stop_reason="tool_use", usage=Usage(10, 10))
