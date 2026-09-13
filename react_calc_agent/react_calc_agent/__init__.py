"""ReAct Calculator Agent — 5 lớp: prompt / model / middleware / state / tool."""

from .agent import ReActAgent
from .middleware import (
    MathIntentRouter,
    Middleware,
    NumberGroundingGuard,
    ToolGuard,
    TracingMiddleware,
    default_middleware,
)
from .model import AnthropicModel, FakeModel, ModelRequest, ModelResponse, text_response, tool_use_response
from .prompt import SYSTEM_PROMPT, build_system_prompt
from .state import AgentState, ToolCall, Usage
from .tools import CalculationError, Tool, ToolRegistry, default_registry, safe_eval

__version__ = "1.0.0"

__all__ = [
    "ReActAgent",
    "AgentState",
    "ToolCall",
    "Usage",
    "Tool",
    "ToolRegistry",
    "default_registry",
    "safe_eval",
    "CalculationError",
    "AnthropicModel",
    "FakeModel",
    "ModelRequest",
    "ModelResponse",
    "text_response",
    "tool_use_response",
    "Middleware",
    "MathIntentRouter",
    "NumberGroundingGuard",
    "ToolGuard",
    "TracingMiddleware",
    "default_middleware",
    "SYSTEM_PROMPT",
    "build_system_prompt",
]
