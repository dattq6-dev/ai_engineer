# Kiến trúc — ReAct Calculator Agent

> Tài liệu thiết kế. Giải thích **vì sao** mỗi lớp tồn tại, ranh giới trách nhiệm,
> và những đánh đổi đã chọn. Phần "học khái niệm" nằm ở [GIAI-THICH.md](GIAI-THICH.md).

---

## 1. Vấn đề cần giải

Một LLM sinh văn bản bằng cách dự đoán token tiếp theo. Khi nó "tính" `1234567 × 7654321`,
nó không thực hiện phép nhân — nó sinh ra dãy chữ số *trông giống* kết quả của phép nhân đó.
Với số nhỏ, dãy quen thuộc trong dữ liệu huấn luyện nên thường đúng. Với số lớn,
các chữ số ở giữa là nơi sai nhiều nhất, và **sai một cách tự tin**.

Với hệ thống ngân hàng, "tự tin nhưng sai" là chế độ hỏng nguy hiểm nhất: không có
exception, không có stack trace, chỉ có một con số sai nằm im trong báo cáo.

Giải pháp kiến trúc: **tách suy luận khỏi tính toán**. LLM giữ phần nó giỏi
(hiểu đề, chọn công thức, chọn công cụ, diễn giải kết quả). Python giữ phần LLM
không làm được (số học tất định).

---

## 2. Ranh giới 5 lớp

| Lớp | File | Trách nhiệm DUY NHẤT | KHÔNG được làm |
|-----|------|----------------------|----------------|
| Prompt | `prompt.py` | Khai báo hành vi mong muốn bằng ngôn ngữ tự nhiên | Không chứa logic Python |
| Model | `model.py` | Gọi API, chuẩn hoá request/response | Không biết gì về intent hay guard |
| Tool | `tools.py` | Thực thi tính toán tất định, an toàn | Không gọi model, không đọc state |
| State | `state.py` | Lưu trữ + audit trail của một run | Không chứa business logic |
| Middleware | `middleware.py` | Chính sách điều khiển (cắm/rút được) | Không gọi model, không chạy tool |
| Orchestrator | `agent.py` | Ráp vòng lặp, giữ bất biến của API | Không chứa chính sách cụ thể |

Kiểm chứng ranh giới này bằng một câu hỏi: *"Nếu tôi bỏ file X đi, agent còn chạy không?"*
Bỏ `middleware.py` → agent vẫn chạy, chỉ mất kiểm soát. Bỏ `tools.py` → không còn agent.
Đó là dấu hiệu ranh giới đúng.

---

## 3. Hợp đồng với Messages API

Ba điều **bắt buộc đúng**, sai một cái là request kế tiếp bị từ chối
([nguồn](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls)):

**(a) `tool_result` đi trong message role `user`, không phải role `tool`.**

```python
# ĐÚNG
{"role": "user", "content": [
    {"type": "tool_result", "tool_use_id": "toolu_01A...", "content": "17 * 24 = 408"}
]}

# SAI (đây là quy ước của OpenAI, không phải Anthropic)
{"role": "tool", "tool_call_id": "...", "content": "..."}
```

**(b) Mỗi `tool_use.id` phải có đúng một `tool_result.tool_use_id` khớp.**
Khi model gọi song song 3 công cụ, bạn phải trả về đủ 3 block trong **một** user message.
Đây là lý do `agent._execute()` được gọi trong list comprehension rồi mới `append_tool_results`
một lần duy nhất.

**(c) Lỗi tool trả về bằng `is_error: true`, không phải bằng exception.**

```python
{"type": "tool_result", "tool_use_id": "t1",
 "content": "CalculationError: Chia cho 0.", "is_error": True}
```

Nhờ vậy model *đọc được lỗi* và tự sửa tham số ở bước sau — xem
`test_tool_error_is_fed_back_and_recovered`. Nếu bạn để exception bay ra, agent chết
trong khi model hoàn toàn có khả năng tự phục hồi.

`ToolRegistry.invoke()` vì thế **không bao giờ raise** — nó luôn trả `(content, is_error)`.

---

## 4. Cơ chế nhận diện request tính toán

Yêu cầu "agent phải nhận diện request liên quan đến tính toán để không trả lời
randomly" được cài bằng **ba lớp phòng thủ độc lập**, chứ không phải một.

### Lớp 1 — Prompt (ràng buộc mềm)

`SYSTEM_PROMPT` cấm tính nhẩm và mô tả quy trình THINK → ACT → OBSERVE.
Hiệu quả cao nhưng **không có bảo đảm**: model vẫn có xác suất khác 0 để bỏ qua.

### Lớp 2 — `tool_choice` (ràng buộc cứng)

`MathIntentRouter` phân loại request rồi biến kết quả thành tham số API:

```python
tool_choice = {"type": "any"}   # intent = math, chưa có observation -> API BẮT BUỘC sinh tool_use
tool_choice = {"type": "auto"}  # đã có observation, hoặc không phải câu hỏi tính toán
```

Bộ phân loại là **heuristic tất định**, không phải LLM — chạy 0 token, 0 độ trễ,
test được bằng `pytest`:

```
biểu thức số học (\d [+-*/^] \d)  và không phải câu hỏi khái niệm   -> math
từ khoá toán (tính/tổng/lãi/average/...) VÀ có số trong câu         -> math
từ khoá khái niệm (là gì/giải thích/what is) VÀ không có số         -> non_math
từ khoá toán nhưng KHÔNG có số  ("tính lãi suất thế nào?")          -> unknown  (để model tự quyết)
có số nhưng không có từ khoá nào ("gọi số 0901234567")              -> unknown
còn lại                                                             -> non_math
```

**Điểm chết người phải tránh:** nếu ép `{"type": "any"}` ở *mọi* bước, agent sẽ
không bao giờ kết luận được — model buộc phải gọi tool mãi cho tới khi hết
`max_steps`. Vì vậy router **nhả ra `auto` ngay khi đã có một observation thành công**.
Test `test_no_infinite_force_loop` khoá hành vi này lại.

### Lớp 3 — `NumberGroundingGuard` (hậu kiểm)

Ở lượt kết luận, guard trích mọi con số trong câu trả lời và kiểm tra xem chúng có
truy vết được về (a) đề bài, (b) tham số đưa vào tool, hay (c) output tool không.
Không truy vết được → tiêm một user message sửa lỗi và bắt agent chạy lại.

```
                           ┌──────────────────────┐
 câu trả lời cuối ────────►│ trích số trong answer│
                           └──────────┬───────────┘
                                      ▼
                     mọi số ∈ verified_numbers (có làm tròn)?
                          │                        │
                        CÓ│                        │KHÔNG
                          ▼                        ▼
                       chấp nhận          retries_used < max_retries?
                                              │            │
                                            CÓ│            │KHÔNG
                                              ▼            ▼
                                   tiêm correction   fail-open + warnings[]
                                   + chạy lại        (hoặc fail-closed nếu strict=True)
```

Việc so khớp số phải xử lý cả định dạng Việt Nam lẫn Anh Mỹ:

```
"1.234.567" -> 1234567     "1,5"      -> 1.5
"1,234,567" -> 1234567     "1.234,56" -> 1234.56
```

Quy tắc: *dấu phân cách xuất hiện cuối cùng là dấu thập phân, trừ khi nó chia phần
đuôi thành đúng nhóm 3 chữ số*.

> **Hai lỗi thật đã gặp khi viết guard này** (đều đã có regression test):
> 1. Regex `\d[\d.,]*` nuốt luôn dấu chấm cuối câu: `"là 408."` → token `"408."` →
>    parse lỗi → số bị bỏ qua → guard **im lặng cho qua số bịa**. Guard hỏng theo
>    kiểu âm thầm là guard nguy hiểm hơn không có guard.
> 2. Lookahead `(?![\w])` làm regex backtrack ở `"1.250.000đ"` và cắt còn `1.250`.
>    Tiền tệ Việt Nam viết dính đuôi là ca thực tế, không phải ca hiếm.

---

## 5. Đánh đổi đã chọn (và vì sao)

| Quyết định | Được | Mất | Vì sao vẫn chọn |
|---|---|---|---|
| `tool_choice="any"` khi intent=math | Bảo đảm cứng, không phụ thuộc model ngoan | Model không hỏi lại được ở bước 1 khi đề thiếu dữ kiện | Chỉ ép khi câu hỏi **đã có ít nhất 1 con số**; câu thiếu dữ kiện hoàn toàn vẫn đi nhánh `auto` |
| Guard **fail-open** sau N retry | Không chặn oan người dùng | Có thể lọt số sai | Luôn ghi `state.warnings` → giám sát bắt được; đặt `strict=True` khi cần fail-closed |
| Phân loại intent bằng heuristic | 0 token, tất định, test được | Không hiểu ngữ cảnh sâu | Đây là lớp *định tuyến*, không phải lớp *quyết định cuối*; sai thì lớp 3 đỡ |
| AST allow-list thay vì `eval()` | Không có RCE | Chỉ hỗ trợ toán học thuần | `eval()` trên chuỗi do LLM sinh ra là lỗ hổng thực thi mã từ xa |
| `FakeModel` cùng interface | Test toàn vòng lặp: 0 token, 0.1 giây, tất định | Phải tự chuẩn hoá response | CI không có secret; test có LLM thật thì flaky và tốn tiền |
| `temperature=0.0` mặc định | Giảm phương sai chọn công cụ | Ít đa dạng diễn đạt | Agent tính toán cần tái lập được, không cần sáng tạo |

---

## 6. Chế độ hỏng & cách hệ thống đỡ

| Chế độ hỏng | Biểu hiện | Cơ chế đỡ | Test |
|---|---|---|---|
| Model bịa số | Số không có trong tool output | `NumberGroundingGuard` retry | `test_hallucinated_number_triggers_retry_and_is_corrected` |
| Model gọi tool không tồn tại | `tool_use.name` lạ | `ToolGuard` → `tool_result(is_error)` | `test_blocked_tool_returns_error_block_not_crash` |
| Log ghi sai trạng thái | Trace in `tool_choice` nửa chừng | `TracingMiddleware` đặt trong cùng | `test_tracing_sees_the_real_tool_choice` |
| Model lặp vô hạn | Luôn trả `stop_reason=tool_use` | `max_steps` → `status="halted"` | `test_step_budget_halts_infinite_loop` |
| Model gọi lại y hệt | Tốn token, không tiến triển | `ToolGuard.block_duplicates` | `test_tool_guard_blocks_duplicate_call` |
| Tool ném exception | Agent chết giữa chừng | `ToolRegistry.invoke` không bao giờ raise | `test_registry_never_raises` |
| API lỗi / rate limit | Exception bay ra ngoài | try/except → `status="failed"` | `test_model_exception_is_contained` |
| Prompt injection qua biểu thức | RCE | AST allow-list | `test_safe_eval_blocks_code_execution` |
| Biểu thức gây treo | `2**10000000` | Chặn số mũ & độ dài | `test_safe_eval_blocks_dos` |

---

## 7. Đưa lên production còn thiếu gì

Khung này là **đúng về kiến trúc** nhưng chưa **đủ cho production**. Cần bổ sung:

1. **Retry + backoff** cho lỗi `429` / `529` ở tầng `AnthropicModel` (SDK có `max_retries`).
2. **Streaming** nếu cần hiển thị THOUGHT theo thời gian thực.
3. **Prompt caching** cho `system` + `tools` — hai khối này lặp lại ở *mọi* bước của
   *mọi* run, là chỗ tiết kiệm chi phí lớn nhất.
4. **Hội thoại nhiều lượt**: hiện `run()` tạo state mới mỗi lần; muốn giữ ngữ cảnh
   thì cần lớp lưu `messages` giữa các lượt + chính sách cắt bớt lịch sử.
5. **Persist trace** ra kho log tập trung — `state.trace` đang chỉ nằm trong bộ nhớ.
6. **Đo lường**: tỷ lệ gọi tool trên câu hỏi math, tỷ lệ guard retry, tỷ lệ
   `warnings` khác rỗng. Ba chỉ số này là đèn báo sức khoẻ của agent.
7. **Định danh & phân quyền** nếu thêm công cụ chạm dữ liệu khách hàng.

---

## Nguồn

- Yao et al., *ReAct: Synergizing Reasoning and Acting in Language Models*, ICLR 2023 — <https://arxiv.org/abs/2210.03629>
- Anthropic, *Tool use overview* — <https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview>
- Anthropic, *Handle tool calls* — <https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls>
- Anthropic, *Model IDs and versioning* — <https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions>
