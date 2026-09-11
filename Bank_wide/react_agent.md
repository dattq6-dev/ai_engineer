Xây dựng một ReAct Agent hỗ trợ giải toán đơn giản:

Bạn cần xây dựng một ReAct agent có khả năng tiếp nhận câu hỏi toán học bằng ngôn ngữ tự nhiên (tiếng Việt), suy luận từng bước và sử dụng công cụ tính toán để đưa ra câu trả lời chính xác.
Agent được triển khai bằng LangChain (và LangGraph nếu muốn mở rộng).

YÊU CẦU CHỨC NĂNG
Agent phải:

Nhận câu hỏi toán bằng văn bản
Ví dụ:

5 + 7 là bao nhiêu?
(12 + 8) * 3 bằng bao nhiêu?
Tôi có 10 quả táo, cho đi 3, còn lại bao nhiêu?

Thực hiện ReAct reasoning, gồm các bước:

Thought (suy nghĩ)
Action (chọn công cụ)
Observation (kết quả từ công cụ)
Final Answer (trả lời cuối)

Biết khi nào cần gọi tool tính toán, không trả lời ngẫu nhiên.
