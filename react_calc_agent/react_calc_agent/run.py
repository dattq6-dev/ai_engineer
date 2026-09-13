"""
CLI demo.

    export ANTHROPIC_API_KEY=sk-ant-...
    python -m react_calc_agent.run "1234567 nhân 7654321 bằng bao nhiêu?"
    python -m react_calc_agent.run --demo          # chạy bộ ví dụ offline (FakeModel)
    python -m react_calc_agent.run --repl
"""

from __future__ import annotations

import argparse
import json
import sys

from .agent import ReActAgent
from .middleware import MathIntentRouter


def _print_state(state, show_trace: bool) -> None:
    print("\n" + "=" * 68)
    print("TRẢ LỜI:", state.final_answer)
    print("-" * 68)
    print(f"intent={state.intent}  status={state.status}  steps={state.step}  "
          f"tools={len(state.tool_calls)}  tokens={state.usage.as_dict()['total_tokens']}")
    for c in state.tool_calls:
        flag = "ERR" if c.is_error else "OK "
        print(f"  [{flag}] {c.name}({json.dumps(c.input, ensure_ascii=False)}) -> {c.output}")
    if state.warnings:
        print("  CẢNH BÁO:", state.warnings)
    if show_trace:
        print("-" * 68)
        for ev in state.trace:
            print(" ", json.dumps(ev, ensure_ascii=False, default=str))
    print("=" * 68)


def _demo_offline() -> None:
    """Chạy được ngay cả khi không có API key — dùng để kiểm tra bộ phân loại intent."""
    samples = [
        "Tính giúp tôi 17 * 24",
        "1234567 nhân 7654321 bằng bao nhiêu?",
        "Khách vay 1.250.000.000 VND lãi suất 9,6%/năm trong 240 tháng, mỗi tháng trả bao nhiêu?",
        "Trung bình của 12, 15, 19, 22 là bao nhiêu?",
        "ReAct agent là gì?",
        "Giải thích khái niệm lãi kép",
        "Viết giúp tôi một email cảm ơn khách hàng",
    ]
    print(f"{'INTENT':<10} {'ÉP TOOL':<9} CÂU HỎI")
    print("-" * 90)
    for s in samples:
        intent, _ = MathIntentRouter.classify(s)
        forced = "any" if intent == "math" else "auto"
        print(f"{intent:<10} {forced:<9} {s}")
    print("\n(Đây là demo offline của lớp router. Đặt ANTHROPIC_API_KEY để chạy agent thật.)")


def main() -> int:
    ap = argparse.ArgumentParser(description="ReAct Calculator Agent")
    ap.add_argument("question", nargs="*", help="Câu hỏi")
    ap.add_argument("--demo", action="store_true", help="Demo phân loại intent, không cần API key")
    ap.add_argument("--repl", action="store_true", help="Chế độ hội thoại")
    ap.add_argument("--trace", action="store_true", help="In toàn bộ trace")
    ap.add_argument("--quiet", action="store_true", help="Tắt log từng bước")
    ap.add_argument("--max-steps", type=int, default=8)
    args = ap.parse_args()

    if args.demo:
        _demo_offline()
        return 0

    agent = ReActAgent(max_steps=args.max_steps, verbose=not args.quiet)

    if args.repl:
        print("Gõ câu hỏi, Ctrl-C để thoát.")
        while True:
            try:
                q = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                return 0
            if q:
                _print_state(agent.run(q), args.trace)
        return 0

    if not args.question:
        ap.print_help()
        return 1

    _print_state(agent.run(" ".join(args.question)), args.trace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
