"""Test LỚP TOOL — độ chính xác và độ an toàn."""

import math

import pytest

from react_calc_agent.tools import (
    CalculationError,
    ToolRegistry,
    calculator,
    default_registry,
    safe_eval,
)

# ----------------------------------------------------------------------
# Độ chính xác
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "expr,expected",
    [
        ("2 + 2", 4),
        ("17 * 24", 408),
        ("1234567 * 7654321", 1234567 * 7654321),
        ("(1250000 * 0.085) / 12", (1250000 * 0.085) / 12),
        ("2 ** 10", 1024),
        ("sqrt(144)", 12),
        ("round(10/3, 4)", round(10 / 3, 4)),
        ("log(e)", 1.0),
        ("factorial(20)", math.factorial(20)),
        ("100 * (1.075 ** 10 - 1)", 100 * (1.075**10 - 1)),
        ("7 % 3", 1),
        ("7 // 2", 3),
        ("2 ^ 8", 256),          # ^ được chuẩn hoá thành **
        ("12 × 12", 144),        # ký hiệu tiếng Việt
        ("144 ÷ 12", 12),
    ],
)
def test_safe_eval_accuracy(expr, expected):
    assert safe_eval(expr) == pytest.approx(expected)


def test_big_integer_is_exact_not_float():
    """Điểm cốt lõi: công cụ cho SỐ NGUYÊN CHÍNH XÁC, không phải xấp xỉ."""
    out = safe_eval("123456789 * 987654321")
    assert out == 123456789 * 987654321
    assert isinstance(out, int)


# ----------------------------------------------------------------------
# An toàn — đây là lý do không dùng eval()
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "payload",
    [
        "__import__('os').system('ls')",
        "open('/etc/passwd').read()",
        "(lambda: 1)()",
        "[x for x in range(10)]",
        "().__class__.__bases__",
        "exec('print(1)')",
        "a = 5",
        "print(1)",
        "globals()",
        "2 if True else 3",
    ],
)
def test_safe_eval_blocks_code_execution(payload):
    with pytest.raises(CalculationError):
        safe_eval(payload)


@pytest.mark.parametrize("payload", ["2 ** 10000000", "factorial(100000)", "x" * 600])
def test_safe_eval_blocks_dos(payload):
    with pytest.raises(CalculationError):
        safe_eval(payload)


def test_division_by_zero_is_recoverable_error():
    with pytest.raises(CalculationError, match="Chia cho 0"):
        safe_eval("1/0")


# ----------------------------------------------------------------------
# Registry: lỗi phải quay về model, không được làm sập run
# ----------------------------------------------------------------------


def test_registry_never_raises():
    reg = default_registry()
    content, is_error = reg.invoke("calculator", {"expression": "1/0"})
    assert is_error is True and "Chia cho 0" in content

    content, is_error = reg.invoke("khong_ton_tai", {})
    assert is_error is True and "ToolNotFound" in content

    content, is_error = reg.invoke("calculator", {"sai_tham_so": 1})
    assert is_error is True


def test_api_spec_matches_anthropic_contract():
    """Spec gửi lên API phải có ĐÚNG 3 khoá: name / description / input_schema."""
    for spec in default_registry().api_specs():
        assert set(spec) == {"name", "description", "input_schema"}
        assert spec["input_schema"]["type"] == "object"
        assert "properties" in spec["input_schema"]


def test_duplicate_tool_name_rejected():
    reg = ToolRegistry([calculator])
    with pytest.raises(ValueError):
        reg.register(calculator)


# ----------------------------------------------------------------------
# Tool nghiệp vụ ngân hàng — đối chiếu công thức annuity chuẩn
# ----------------------------------------------------------------------


def test_loan_payment_annuity_matches_closed_form():
    reg = default_registry()
    out, is_error = reg.invoke(
        "loan_payment", {"principal": 1_000_000_000, "annual_rate_pct": 9.6, "months": 240}
    )
    assert not is_error
    i = 0.096 / 12
    expected = 1_000_000_000 * i * (1 + i) ** 240 / ((1 + i) ** 240 - 1)
    monthly = float(out.split("monthly_payment=")[1].split()[0])
    assert monthly == pytest.approx(expected, rel=1e-6)


def test_loan_payment_zero_rate():
    out, is_error = default_registry().invoke(
        "loan_payment", {"principal": 1200, "annual_rate_pct": 0, "months": 12}
    )
    assert not is_error and "monthly_payment=100" in out


def test_descriptive_stats():
    out, is_error = default_registry().invoke("descriptive_stats", {"numbers": [2, 4, 4, 4, 5, 5, 7, 9]})
    assert not is_error
    assert "mean=5" in out and "n=8" in out
