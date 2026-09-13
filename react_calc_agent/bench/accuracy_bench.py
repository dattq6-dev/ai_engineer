"""
BENCHMARK — "dùng công cụ" vs "để model tự nhẩm".

Đây là bằng chứng định lượng cho luận điểm trung tâm của dự án: LLM dự đoán token,
nó không tính toán. Cùng một model, cùng một bộ đề, chỉ khác ở chỗ có bật công cụ
hay không.

    export ANTHROPIC_API_KEY=sk-ant-...
    python bench/accuracy_bench.py            # 12 bài, 2 chế độ
    python bench/accuracy_bench.py --repeat 3 # lặp 3 lần để thấy tính bất ổn định
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from react_calc_agent import ReActAgent, default_registry  # noqa: E402
from react_calc_agent.middleware import extract_numbers  # noqa: E402
from react_calc_agent.model import AnthropicModel, ModelRequest  # noqa: E402

MODEL_ID = os.getenv("CALCAGENT_MODEL", "claude-sonnet-5")

# (câu hỏi, đáp án đúng tính bằng Python)
CASES: list[tuple[str, Decimal]] = [
    ("1234567 nhân 7654321 bằng bao nhiêu?", Decimal(1234567 * 7654321)),
    ("98765 * 43210 bằng bao nhiêu?", Decimal(98765 * 43210)),
    ("Tính 847293 + 958174 + 273846", Decimal(847293 + 958174 + 273846)),
    ("Tính 2^37", Decimal(2**37)),
    ("19! bằng bao nhiêu?", Decimal(1) * __import__("math").factorial(19)),
    ("Tính 7919 * 7907", Decimal(7919 * 7907)),
    ("123456789 chia 3607 được bao nhiêu (lấy phần nguyên)?", Decimal(123456789 // 3607)),
    ("Tính 45678 * 98765 - 12345678", Decimal(45678 * 98765 - 12345678)),
    ("Tổng các số từ 1 đến 4567 là bao nhiêu?", Decimal(4567 * 4568 // 2)),
    ("Tính 3.14159 * 2718 * 1414 (làm tròn phần nguyên)", Decimal(round(3.14159 * 2718 * 1414))),
    ("Một khoản 1250000 tăng 8.5% mỗi năm trong 7 năm thì thành bao nhiêu (làm tròn phần nguyên)?",
     Decimal(round(1250000 * 1.085**7))),
    ("Tính 999983 * 999979", Decimal(999983 * 999979)),
]


def contains_answer(text: str, expected: Decimal) -> bool:
    """Đáp án đúng phải xuất hiện trong câu trả lời, chấp nhận mọi cách nhóm chữ số."""
    if not text:
        return False
    exp = str(expected)
    flat = re.sub(r"[.,\s_]", "", text)
    if exp in flat:
        return True
    return any(n == expected for n in extract_numbers(text))


def run_with_tools(question: str) -> tuple[str, int, float]:
    agent = ReActAgent(model=AnthropicModel(model=MODEL_ID), verbose=False)
    t0 = time.time()
    st = agent.run(question)
    return st.final_answer or "", st.usage.as_dict()["total_tokens"], time.time() - t0


def run_without_tools(question: str) -> tuple[str, int, float]:
    """Cùng model, cùng nhiệt độ 0, nhưng KHÔNG có công cụ — bắt buộc phải nhẩm."""
    model = AnthropicModel(model=MODEL_ID)
    t0 = time.time()
    resp = model.invoke(
        ModelRequest(
            system="Bạn là trợ lý toán học. Trả lời NGẮN GỌN, chỉ nêu kết quả cuối cùng.",
            messages=[{"role": "user", "content": [{"type": "text", "text": question}]}],
            tools=[],
            max_tokens=1024,
        )
    )
    u = resp.usage.as_dict()
    return resp.text(), u["total_tokens"], time.time() - t0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeat", type=int, default=1)
    args = ap.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Cần ANTHROPIC_API_KEY.")
        return 1

    print(f"Model: {MODEL_ID}   |   {len(CASES)} bài × {args.repeat} lượt × 2 chế độ\n")
    score = {"tool": 0, "no_tool": 0}
    tokens = {"tool": 0, "no_tool": 0}
    secs = {"tool": 0.0, "no_tool": 0.0}
    total = len(CASES) * args.repeat

    header = f"{'#':<3} {'TOOL':<6} {'NHẨM':<6} CÂU HỎI"
    print(header)
    print("-" * 96)

    for r in range(args.repeat):
        for idx, (q, expected) in enumerate(CASES, 1):
            a1, t1, s1 = run_with_tools(q)
            ok1 = contains_answer(a1, expected)
            a2, t2, s2 = run_without_tools(q)
            ok2 = contains_answer(a2, expected)

            score["tool"] += ok1
            score["no_tool"] += ok2
            tokens["tool"] += t1
            tokens["no_tool"] += t2
            secs["tool"] += s1
            secs["no_tool"] += s2

            print(f"{idx:<3} {'✓' if ok1 else '✗':<6} {'✓' if ok2 else '✗':<6} {q[:64]}")
            if not ok1:
                print(f"      -> tool sai:  {a1[:140]}")
            if not ok2:
                print(f"      -> nhẩm sai:  {a2[:140]}  (đúng: {expected})")

    print("-" * 96)
    for mode, label in (("tool", "CÓ công cụ"), ("no_tool", "KHÔNG công cụ")):
        acc = score[mode] / total * 100
        print(
            f"{label:<16} đúng {score[mode]}/{total} ({acc:.1f}%)   "
            f"tokens={tokens[mode]:<7} thời gian={secs[mode]:.1f}s"
        )
    print(
        "\nDiễn giải: chênh lệch độ chính xác chính là phần 'suy luận xác suất' bị thay bằng "
        "'thực thi tất định'. Chi phí phải trả là thêm token và thêm độ trễ round-trip."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
