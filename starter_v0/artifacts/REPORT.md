# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team:
- Members:
- Provider/model: OpenRouter / `openai/gpt-4o-mini`

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent tra cứu web/tin tức, tìm bài đăng mạng xã hội và paper arXiv, đọc URL, tìm trong policy nội bộ rồi tổng hợp kết quả có nguồn. Tool gửi Telegram có sẵn; UI demo khóa gửi mặc định và yêu cầu bật xác nhận rõ ràng.

**Link dùng thử (deploy):**

> URL local cho phiên dev hiện tại; chưa phải link public:
>
> http://localhost:8501

## A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
| timeline | lấy bài đăng gần đây từ một tài khoản | không |
| social_search | tìm bài đăng theo chủ đề | không |
| lookup | tra cứu web và tin tức | không |
| fetch | đọc nội dung từ URL | không |
| format | định dạng các kết quả thành digest | không |
| send | gửi nội dung lên Telegram khi được xác nhận | không |
| policy | tìm trong policy nội bộ | không |
| papers | tìm paper trên arXiv | không |
| paper_text | trích văn bản paper arXiv | không |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1. Tìm 2 tin mới trong tuần này về mô hình ngôn ngữ mã nguồn mở.
2. Tra cứu policy data privacy nội bộ: nêu quy tắc chính khi xử lý dữ liệu cá nhân.
3. Tìm 2 bài nghiên cứu trên arXiv về đánh giá khả năng tool-calling của LLM.
4. Đọc một URL cụ thể và tóm tắt các ý chính kèm nguồn.

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Bản đo trước tối ưu prompt/tool | — | case 0.70; routing 0.75; args 0.70; multiturn 1.00 | [v0 run](../runs/v0_B_base_openrouter_20261110T032941707184.json) |
| v1 | — | Chưa có run | — | — | — |
| v2 | — | Chưa có run | — | — | — |
| v3 | — | Chưa có run | — | — | — |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `send` | Gọi send thay vì trả lời không dùng tool | Bổ sung ranh giới ngoài phạm vi; không gửi nếu user không yêu cầu |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | Đoán tài khoản thay vì gọi clarify | Hỏi người dùng khi thiếu account |
| R11_missing_url | missing_info | `fetch(url="https://example.com/article")` | Bịa URL thay vì hỏi lại | Hỏi URL cụ thể, không tự đoán |
| R12_confirm_before_send | wrong_boundary | `send` | Gọi send khi chưa có xác nhận | Yêu cầu xác nhận rõ trước hành động |
| R13_parallel_web_and_tweets | wrong_tool | `lookup`, `social_search` | Lookup thiếu `topic=news`; query là `AI news` thay vì `AI` | Làm rõ routing và quy ước đối số trong prompt/tool descriptions |
| R14_out_of_scope_coding | out_of_scope | `send` | Gọi send cho yêu cầu code ngoài phạm vi | Không gọi action tool cho yêu cầu không gửi |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| — | Chưa thêm case; `data/eval_group.json` hiện có danh sách rỗng | Cần thêm 10 case (5 single-turn, 5 multi-turn) | Chưa chạy |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tìm 2 bài nghiên cứu trên arXiv về đánh giá khả năng tool-calling của LLM | `papers` | v0, OpenRouter / `openai/gpt-4o-mini` | Không tìm thấy kết quả với truy vấn này |
| 2 | Tra cứu policy data privacy nội bộ | `policy` | v0 | Trả về quy tắc về dữ liệu mật, transcript và API credentials |
| 3 | Tìm 2 tin mới trong tuần về mô hình ngôn ngữ mã nguồn mở | `lookup` (`news`, sau đó `general`) | v0 | Trả về hai kết quả; agent đã gọi lookup lần thứ hai với topic general |

Transcript: [v0 live chat](../transcripts/v0_openrouter_20261110T033831997671.transcript.json)

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `app.py` | Bị khóa mặc định trong UI | Chỉ thực thi khi bật cho phép và tool call có `confirmed=true` |
| arXiv/company policy | [v0 live chat](../transcripts/v0_openrouter_20261110T033831997671.transcript.json) | `policy` trả được nội dung local; arXiv query thử nghiệm không có kết quả | Cần thử từ khóa paper cụ thể hơn |
| UI | [app.py](../app.py), `http://localhost:8501` | Streamlit chạy và trả HTTP 200 | Link chỉ local trong phiên dev, chưa public |
| Tool unit tests (`tests/`) | `pytest -q` | 62 passed, 17 skipped | Các skip là TODO tests chưa triển khai; yêu cầu 0 skipped chưa đạt |

Tool unit tests: số test đã viết, số bug tìm được trong tool có sẵn (nếu có), và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

## B6. Reflection

- `system_prompt.md`: cần định tuyến rõ yêu cầu ngoài phạm vi, hỏi lại khi thiếu account/URL, và không tự gửi.
- `tools.yaml`: cần mô tả rõ `topic=news`, cách đặt query, cùng điều kiện `confirmed=true` cho `send`.
- Cần review thủ công các case hành động gửi, vì chỉ chấm tool/args không xác nhận được người dùng đã đồng ý gửi.
- Tiếp theo: sửa từng giả thuyết, chạy v1–v3 và thêm 10 case vào `eval_group.json`; chưa có bằng chứng cho các phiên bản này.

## B7. Small Local Model Challenge (bonus)

Only fill if your team did the local model challenge.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?
