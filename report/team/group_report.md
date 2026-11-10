# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Mỗi bảng trỏ tới file thật trong repo: run JSON (`starter_v0/runs/`), version log, transcript, eval case.
> Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`. Cách chấm: [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: _Lesongthao_
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v5: cùng model **`gpt-4o-mini`**, temperature 0. v0–v1 chạy qua **OpenRouter** (`openai/gpt-4o-mini`); v2–v5, group và extension chạy qua **OpenAI API trực tiếp** (`gpt-4o-mini`). Chi tiết trong [version_log.csv](../../starter_v0/artifacts/version_log.csv).

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

**Research agent cho tin công nghệ/AI:** tìm tin trên web, đọc tweet của một người hoặc theo chủ đề, đọc nội dung một URL, tìm paper arXiv, tra Wikipedia, xem Hacker News, tìm repo GitHub và model Hugging Face, tra company policy nội bộ, rồi gom thành bản tin. Agent **hỏi lại khi thiếu thông tin** (không đoán account/URL) và **luôn hỏi xác nhận Có/Không trước khi đăng lên Telegram**.

**Cách chạy UI:**

```bash
cd starter_v0
pip install -r requirements.txt      # đã gồm streamlit
cp .env.example .env                 # điền OPENROUTER_API_KEY (hoặc OPENAI_API_KEY), TAVILY_API_KEY, FIRECRAWL_API_KEY, RAPIDAPI_KEY
streamlit run app.py                 # http://localhost:8501
# public link tạm: cloudflared tunnel --url http://localhost:8501
```

UI (`starter_v0/app.py`): chat nhiều lượt dùng đúng vòng lặp tool của `chat.py`, hiển thị từng tool call + args + kết quả (lỗi tool được đánh dấu ⚠️, không bị ẩn), nút ✅/❌ khi agent chờ xác nhận gửi, tự lưu `transcripts/ui_*.transcript.json`.

**Link dùng thử (deploy):**

> URL: https://automatic-parakeet-74ggpp7g59p2vx5-8501.app.github.dev/ — GitHub Codespaces port forward, chỉ hoạt động khi codespace đang chạy. Nếu link không mở được, chạy UI theo lệnh ở trên.

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại khi thiếu account/URL (`text`); hỏi Có/Không trước khi gửi (`yes_no`) | không |
| timeline | Tweet mới nhất **của một người** (Sam Altman → `sama`) | không |
| social_search | Tweet **về một chủ đề** (`Latest`/`Top`) | không |
| lookup | Tin tức/thông tin web (Tavily, `topic=news`, `timeframe`) | không |
| fetch | Đọc nội dung một URL (Firecrawl) | không |
| format | Gom item đã có thành bản tin markdown | không |
| send | Đăng Telegram — chỉ khi `confirmed=true` | không |
| policy | Tra company policy nội bộ | không |
| papers / paper_text | Tìm paper arXiv / trích text PDF arXiv | không |
| **wikipedia** | Kiến thức nền: một người/khái niệm/tổ chức là gì (en/vi) | **có** |
| **hackernews** | Thảo luận trên Hacker News (`top`/`latest`, `timeframe`) | **có** |
| **github_repos** | Tìm repo mã nguồn mở (lọc ngôn ngữ, sắp theo sao) | **có** |
| **hf_models** | Tìm model Hugging Face theo task và độ phổ biến | **có** |

### A3. Câu hỏi mẫu để thử

1. `Tin tức AI hôm nay có gì nổi bật?`
2. `Tóm tắt 5 tweet mới nhất giúp mình` → agent hỏi lại tài khoản → `Của Andrej Karpathy nhé`
3. `Tuần này trên Hacker News dân dev bàn gì về Rust?`
4. `Tìm 5 repo GitHub nhiều sao nhất về LLM agent framework`
5. `Đăng bản tin AI hôm nay lên Telegram giúp mình` → agent hỏi Có/Không trước khi gửi

## 3. Giải pháp

- **system_prompt.md** (v1–v3, mỗi version gỡ một chỉ dẫn xấu của starter): v1 bỏ *"Always finish in a single step. Pick one tool"* (cho phép không gọi tool khi ngoài phạm vi, gọi nhiều tool khi cần nhiều nguồn); v2 bỏ *"đừng hỏi lại, cứ đoán"* → `clarify(response_type="text")`; v3 bỏ *"muốn gửi thì cứ gửi"* → `clarify(response_type="yes_no")` trước khi `send`. v5 thêm routing cho 4 tool mới, rule multi-turn và rule gửi/huỷ gửi.
- **tools.yaml** (v4): viết lại description mọi tool theo "làm gì / khi nào dùng / khi nào KHÔNG dùng", convention args (handle không `@`, map tên → handle, `topic=news`, `timeframe`, `search_type=Top`, `query` chỉ là keyword), `clarify.response_type` bắt buộc, `send` chỉ khi `confirmed=true`. v5 khai báo 4 tool mới.
- **Tool mới** (`starter_v0/tools/{wikipedia,hackernews,github_repos,hf_models}/`): API công khai, không cần key; trả item cùng schema `title/url/source/summary`; input xấu (query rỗng, enum sai, `limit` ngoài khoảng) được chuẩn hoá hoặc trả error dict, không raise.
- **Sửa tool có sẵn:** 12 bug tìm bằng regression test (ví dụ `send(confirmed="false")` vẫn gửi; bot token lộ trong error message; `timeline("@sama")`; `limit=-1` mất tweet cuối).
- Snapshot từng version: `starter_v0/artifacts/versions/v0…v5/`; bản cuối = `starter_v0/artifacts/system_prompt.md` + `tools.yaml` (hash `v5+pfd25f1a8bdd8+t4e3180c18921`).

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi starter trước khi sửa | — | 0.70 (14/20) | [v0_B_base_openrouter_…104242979050.json](../../starter_v0/runs/v0_B_base_openrouter_20261110T104242979050.json) |
| v1 | system_prompt.md | Bỏ "pick one tool": R08/R14 hết gọi tool thừa, R13 gọi đủ nguồn | 0.70 | 0.75 (15/20) | [v1_B_base_openrouter_…145322191182.json](../../starter_v0/runs/v1_B_base_openrouter_20261110T145322191182.json) |
| v2 | system_prompt.md | Bỏ "cứ đoán": R10/R11 chuyển sang `clarify` | 0.75 | 0.80 (16/20) | [v2_B_base_openai_…160703839285.json](../../starter_v0/runs/v2_B_base_openai_20261110T160703839285.json) |
| v3 | system_prompt.md | R12 phải `clarify(yes_no)` trước khi gửi | 0.80 | 0.80 (16/20) | [v3_B_base_openai_…095619294467.json](../../starter_v0/runs/v3_B_base_openai_20261110T095619294467.json) |
| v4 | tools.yaml | Description + convention args rõ ràng sửa routing/args, không regression | 0.80 | 0.95 (19/20) | [v4_B_base_openai_…104217023595.json](../../starter_v0/runs/v4_B_base_openai_20261110T104217023595.json) |
| v5 | tools.yaml + system_prompt.md | Thêm 4 tool mới không làm giảm base | 0.95 | **1.00 (20/20)** | [v5_B_base_openai_…110115868139.json](../../starter_v0/runs/v5_B_base_openai_20261110T110115868139.json) |

Mọi run trên: `provider_error_cases = 0`, `measured_cases = total_cases = 20`.

Nhận xét:

- **v0 → v1 — giả thuyết đúng một phần.** R08, R14 chuyển PASS (v0 gọi `send` để trả lời câu toán/code). R13 đã gọi đủ `lookup` + `social_search` nhưng sai args (`query="AI news"`, thiếu `topic=news`) nên vẫn FAIL. Phát sinh regression **M06**: được phép gọi nhiều tool thì model gọi thừa `social_search` ở lượt "bỏ Twitter, chuyển sang web".
- **v1 → v2 — đúng một phần.** R10/R11 không còn đoán (`timeline("sama")`, `fetch("https://www.example.com/article")`) mà gọi `clarify` hỏi đúng phần thiếu, nhưng bỏ trống `response_type` → vẫn FAIL. Routing 0.80 → 0.90. R13 chuyển PASS dù v2 không đổi convention args — nhiều khả năng do dao động giữa lần chạy/provider. `tools_hash` của v2 (`5b22a2476d41`) khác v1 chỉ vì Git trên Windows đổi LF → CRLF; nội dung `tools.yaml` giống v1 (xem [notes_v2.md](../../starter_v0/analysis/notes_v2.md)).
- **v2 → v3 — chưa xác nhận.** R12 không còn gửi ngay mà đã `clarify`, nhưng dùng `response_type="text"` (hỏi nội dung bản tin) thay vì `yes_no` → vẫn FAIL. Tổng giữ 0.80; routing tăng 0.95.
- **v3 → v4 — bước cải thiện lớn nhất, đến từ `tools.yaml`.** Description `clarify` (khi nào `text`/`yes_no`, `response_type` bắt buộc), `send` (chỉ khi `confirmed`), routing khi nào KHÔNG dùng tool sửa cùng lúc R11, R12, M06. Bài học: lỗi `wrong_arg_value` phải sửa ở chỗ model đọc khi điền tham số (parameter description), prompt đơn thuần không đủ.
- **v4 → v5 — giả thuyết đúng.** Thêm 4 tool mới không gây regression; R10 (v4 gọi `social_search(query="")`) cũng PASS ở v5. Group 0.90, extension 0.90.

### B2. Failure Analysis

| Case ID | Failure Type | Actual Tool Calls (run) | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `send(text="Nguyên hàm của x^2 là …")` (v0) | Câu toán lẽ ra không gọi tool | v1: bỏ "pick one tool", ngoài phạm vi → trả lời thẳng |
| R14_out_of_scope_coding | out_of_scope | `send(text="Dưới đây là một hàm Python …")` (v0) | Câu viết code lẽ ra không gọi tool | v1 (như trên) |
| R13_parallel_web_and_tweets | wrong_tool | `lookup(query="AI news", timeframe="day")` + `social_search(query="AI")` (v0, v1) | `query` phải là `AI`, thiếu `topic=news` | PASS từ v2; convention `query` chỉ là keyword + `topic=news` trong tools.yaml v4 |
| R10_missing_handle | missing_info | v0/v1 `timeline(screenname="sama")`; v2/v3 `clarify(question=…)` thiếu `response_type`; v4 `social_search(query="")` | Đoán account → hỏi lại nhưng thiếu arg → gọi sai tool | v2 (hỏi lại) + v4 (`response_type` bắt buộc); PASS ở v5 |
| R11_missing_url | missing_info | v0/v1 `fetch(url="https://www.example.com/article")`; v2/v3 `clarify` thiếu `response_type` | Bịa URL → hỏi lại nhưng thiếu arg | v2 + v4; PASS từ v4 |
| R12_confirm_before_send | wrong_boundary | v0–v2 `send(text="Bản tin …")`; v3 `clarify(response_type="text")` | Gửi ngay không xác nhận → hỏi nội dung thay vì Có/Không | v3 (rule xác nhận) + v4 (description `send`/`clarify`); PASS từ v4 |
| M06_switch_tool | wrong_tool | `lookup(query="OpenAI", topic="news")` + `social_search(query="OpenAI")` (v1–v3) | Gọi thừa `social_search` sau khi user bảo bỏ Twitter (regression do v1) | v4: description "khi nào KHÔNG dùng" cho `social_search`/`lookup` |
| G10_multiturn_cancel_send (group) | wrong_boundary | `lookup(query="công nghệ", week)` + `lookup(query="AI", week)` (v5) | Gọi `lookup` 2 lần (thừa) sau khi user huỷ đăng | Chưa sửa — đề xuất rule "một request = một lần gọi mỗi tool" |
| E06_briefing_live_plus_style (extension) | wrong_tool | `policy(policy_area="source_citation")` (v5) | Thiếu `lookup` tin AI hôm nay — model hiểu "kiểm tra policy trước" là chỉ làm bước policy | Chưa sửa — đề xuất ví dụ "X nhưng kiểm tra Y trước → gọi cả hai" |

Phân tích chi tiết từng version: [v0_comparison.md](../../starter_v0/analysis/v0_comparison.md), [notes_v1.md](../../starter_v0/analysis/notes_v1.md) … [notes_v5.md](../../starter_v0/analysis/notes_v5.md).

### B3. Team Eval Cases

10 case trong [eval_group.json](../../starter_v0/data/eval_group.json) (5 single + 5 multi), chạy ở [v5_B_group_openai_…110424113208.json](../../starter_v0/runs/v5_B_group_openai_20261110T110424113208.json): **9/10 PASS** (routing 0.90, args 0.90, multiturn 0.80).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_wikipedia_vi_concept (single) | Khái niệm + Wikipedia tiếng Việt → tool mới | `wikipedia(lang="vi")` | PASS |
| G02_hackernews_top_week (single) | HN thay vì Twitter; "tuần này", "nhiều điểm nhất" | `hackernews(query="Rust", sort="top", timeframe="week")` | PASS |
| G03_github_top_stars (single) | Tìm repo, "5 repo", "nhiều sao nhất" | `github_repos(sort="stars", limit=5)` | PASS |
| G04_hf_models_task (single) | Model Hugging Face theo task, "tải nhiều nhất" | `hf_models(task="text-to-image", sort="downloads")` | PASS |
| G05_arxiv_newest_sort (single) | "paper mới nhất" | `papers(sort_by="submittedDate")` | PASS |
| G06_multiturn_github_fill_language (multi) | Carry chủ đề + thêm filter ngôn ngữ + sort | `github_repos(language="Rust", sort="stars")` | PASS |
| G07_multiturn_send_after_yes (multi) | Đã hỏi xác nhận, user nói "Có" | `send(text=…, confirmed=true)` | PASS |
| G08_multiturn_twitter_to_hn (multi) | Bỏ Twitter → HN, giữ chủ đề, "mới nhất" | `hackernews(query="Claude", sort="latest")` | PASS |
| G09_multiturn_wiki_correction (multi) | Sửa người + chọn bản tiếng Anh | `wikipedia(query="Geoffrey Hinton", lang="en")` | PASS |
| G10_multiturn_cancel_send (multi) | User huỷ đăng, chuyển sang tìm web | `lookup(topic="news", timeframe="week")`, không `send` | FAIL (gọi `lookup` 2 lần) |

Extension eval (policy + arXiv): [v5_B_extension_openai_…110514233130.json](../../starter_v0/runs/v5_B_extension_openai_20261110T110514233130.json) — 9/10 PASS (E06 FAIL, xem B2).

### B4. Live Chat Evidence

Transcript chính: [v5_openrouter_20261110T165629438183.transcript.json](../../starter_v0/transcripts/v5_openrouter_20261110T165629438183.transcript.json) — `v5+pfd25f1a8bdd8+t4e3180c18921` (cùng hash với v5 cuối), chạy bằng vòng lặp tool của `chat.py` (`scripts/run_chat_demo.py`), OpenRouter `openai/gpt-4o-mini`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tin tức AI hôm nay có gì nổi bật? | `lookup` | v5 | Trả danh sách tin có link nguồn — **yêu cầu thường** |
| 2 | Tóm tắt 5 tweet mới nhất giúp mình | `timeline(screenname="OpenAI", limit=5)` → `clarify(response_type="yes_no")` | v5 | Agent **đoán account** OpenAI trước khi hỏi lại — cùng lỗi với R10, eval base v5 không bắt được ở lần chạy này |
| 3 | Của Andrej Karpathy nhé | `timeline(screenname="karpathy", limit=5)` | v5 | **User bổ sung thông tin**, agent gọi đúng tool/handle; tool báo lỗi (thiếu `RAPIDAPI_KEY`) và agent nói rõ lỗi |
| 4 | Đăng tóm tắt 5 tweet đó lên Telegram giúp mình | `clarify(response_type="yes_no")` | v5 | **Yêu cầu gửi/đăng** → hỏi xác nhận Có/Không, không gửi ngay |
| 5 | Có, mình xác nhận, đăng đi | `send(confirmed=true, text=…)` | v5 | Chỉ gửi sau khi user đồng ý; `send` lỗi vì chưa cấu hình Telegram → **không có gì bị đăng thật** |
| 6 | Tuần này trên Hacker News dân dev bàn gì về AI agents? | `hackernews(query="AI agents", sort="top", timeframe="week", limit=5)` | v5 | Tool mới trả 5 bài kèm điểm/bình luận/link |

Ghi chú: [ui_v5_openrouter_20261110T091152890665.transcript.json](../../starter_v0/transcripts/ui_v5_openrouter_20261110T091152890665.transcript.json) (UI, 4 lượt) chỉ gồm yêu cầu gửi và có `artifact_version` mang nhãn v5 nhưng hash prompt của v1 → không dùng làm bằng chứng chính.

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) | `starter_v0/tools/{wikipedia,hackernews,github_repos,hf_models}/` (`tool.py` + `TOOL.md`), đăng ký trong `tools/__init__.py` và `artifacts/tools.yaml` | 4 tool API công khai, schema item thống nhất; G01–G04, G06, G08, G09 route đúng | Query rỗng → error dict không gọi mạng; enum sai → mặc định; `limit` bị clamp; `GITHUB_TOKEN` không bao giờ xuất hiện trong kết quả |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py` (15 test cho 4 tool); chạy `cd starter_v0 && pytest` | Toàn suite trên `main` hiện tại: **124 passed, 0 failed, 0 skipped** ([pytest_after_fix.txt](../../starter_v0/analysis/pytest_after_fix.txt) ghi ở thời điểm P5, trước khi thêm tool mới: 89 passed) | Offline hoàn toàn (`fake_http`), không gọi mạng thật, không tốn credit |
| UI (lệnh chạy + link dùng thử) | `starter_v0/app.py`, `requirements.txt` (streamlit), lệnh ở A1, transcript B4 | Chat nhiều lượt, hiện tool call/args/kết quả, nút ✅/❌ xác nhận gửi, lưu transcript | Key chỉ đọc từ `.env`; lỗi tool hiển thị ⚠️ (không ẩn); lỗi provider hiện thông báo thay vì crash |

Tool unit tests: `test_tools_todo.py` có 42 test (14 stub TODO, 15 test tool mới, 13 regression test). Ví dụ lỗi unit test bắt được mà eval không bắt được: `send(confirmed="false")` — chuỗi khác rỗng là truthy nên tool starter **vẫn đăng bài thật**; eval chỉ báo sai arg, còn side effect đã xảy ra.

### B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 | Chưa đạt: chỉ có 1 run local hợp lệ trên cloud; run Ollama không hợp lệ | — |
| Hơn 3 tool mới (≥ 4) | 4 thư mục tool, `tools/__init__.py`, `tools.yaml`, 15 test, case G01–G04/G06/G08/G09 | Mỗi tool có `TOOL.md`, đăng ký, ≥ 3 test và ít nhất 1 eval case route tới | Description có "khi nào KHÔNG dùng" để không cướp routing của `lookup`/`social_search` (v5 base 20/20) |
| `send` gửi thật lên Telegram sau xác nhận | transcript B4 lượt 4–5 | Quy trình hỏi → xác nhận → `send(confirmed=true)` đúng | **Chưa đạt**: không có `status: sent` vì chưa cấu hình bot Telegram |
| Test challenge (0 skipped / regression test) | [pytest_before_fix.txt](../../starter_v0/analysis/pytest_before_fix.txt), [pytest_after_fix.txt](../../starter_v0/analysis/pytest_after_fix.txt) | 0 skipped; 13 regression test FAIL trên code starter, PASS sau khi sửa | Test chạy offline |

Test challenge — 12 bug trong tool có sẵn: `send` (`confirmed="false"` vẫn gửi; thiếu `awaiting_user` khiến chat lặp; bot token lộ trong error; Markdown lỗi làm Telegram từ chối), `timeline` (`@sama`), `timeline`/`social_search` (`limit=-1` mất tweet cuối, `limit=0` → 5), `social_search` (`top` thường), `lookup` (`max_results=50`, `timeframe="today"`, `topic="News"`), `fetch` (URL rỗng vẫn tốn credit; thiếu `https://`), `format` (item là chuỗi gây crash; dấu `-` thừa), `clarify` (`response_type` ngoài enum). Mỗi bug có một regression test trong `test_tools_todo.py`.

### B7. Small Local Model Challenge (bonus)

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v5 | gpt-4o-mini (OpenAI) | v5 | 1.00 | 1.00 | 1.00 | 1.00 | [v5_B_base_openai_…](../../starter_v0/runs/v5_B_base_openai_20261110T110115868139.json) |
| v5-qwen7b | qwen2.5:7b (Ollama) | v5 | **không hợp lệ** | — | — | — | [v5-qwen7b_B_base_ollama_…](../../starter_v0/runs/v5-qwen7b_B_base_ollama_20261110T123327950590.json) — 20/20 `provider_error` (`llama-server process has terminated`) |
| v5-local-on-cloud | gpt-4o-mini (OpenRouter) | `artifacts/local/v5-local` | 0.95 | 0.95 | 0.95 | 0.83 | [v5-local-on-cloud_B_base_openrouter_…](../../starter_v0/runs/v5-local-on-cloud_B_base_openrouter_20261110T113642425557.json) |

Không có run local hợp lệ nên **không đếm được lỗi đặc thù của model nhỏ** và nhóm **không nhận bonus này**.

- Kiểm tra ngược: prompt rút gọn cho local (6 tool, few-shot) chạy trên model cloud vẫn đạt 0.95 — chỉ FAIL M06 (gọi thừa `social_search`), tức bản rút gọn mất phần "khi nào KHÔNG dùng" của tools.yaml v4.
- Khi nào chọn local: khi dữ liệu không được rời máy hoặc cần chạy offline; muốn chọn phải có run hợp lệ của ≥ 2 model local trước.

## 5. Khó khăn và cách xử lý

- **Run Ollama lỗi provider** (`llama-server process has terminated`) → không tính run đó; ghi rõ ở B7.
- **RapidAPI bị Cloudflare chặn IP (Error 1015)** khi lấy key → `timeline`/`social_search` trả lỗi thiếu key trong chat live; eval vẫn chấm routing/args nên không ảnh hưởng metric (B4 lượt 3).
- **Hai provider cho cùng model:** v0–v1 qua OpenRouter, v2–v5 qua OpenAI trực tiếp (cùng `gpt-4o-mini`). Ghi rõ trong version log; R13 đổi trạng thái ở v2 dù prompt không đổi convention → coi là dao động, không tính là hiệu quả của v2.
- **Hash `tools.yaml` v2 khác v1** do Git Windows đổi LF → CRLF, nội dung giống nhau ([notes_v2.md](../../starter_v0/analysis/notes_v2.md)).
- **Làm việc nhiều nhánh:** mỗi thành viên commit gói của mình trên nhánh riêng và merge qua PR; một PR tích hợp lớn (Final) được revert để giữ kết quả theo từng thành viên.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- **Fix thuộc `system_prompt.md`:** chính sách hành vi chung — không ép một tool, hỏi lại thay vì đoán, xác nhận trước khi gửi, câu ngoài phạm vi không gọi tool, cách đọc hội thoại nhiều lượt. Bằng chứng: v1 sửa R08/R14; v2 chuyển R10/R11 từ đoán sang hỏi lại.
- **Fix thuộc `tools.yaml`:** tool nào dùng khi nào/khi nào không, convention từng tham số. Bằng chứng: chỉ khi sửa description (v4) thì R11, R12, M06 mới PASS — prompt v2/v3 đã đúng hướng nhưng model vẫn bỏ trống/sai `response_type`.
- **Cần review thủ công:** (1) case `no_tool` chỉ kiểm tra không gọi tool, không chấm câu trả lời; (2) chất lượng câu hỏi `clarify`; (3) nội dung `send`: ở chat live lượt 5, nội dung gửi là **placeholder** ("Nội dung tóm tắt của tweet đầu tiên…") vì `timeline` lỗi — eval vẫn coi là đúng quy trình; (4) tool trả lỗi (thiếu key) nhưng eval vẫn PASS vì chỉ chấm tool call; (5) lượt 2 chat live agent đoán account dù v5 base đạt 20/20 → một lần chạy eval chưa đủ, cần chạy lặp.
- **Nếu có thêm một vòng (v6, một giả thuyết):** R10 — trong description `timeline` cấm đoán account mặc định và thêm ví dụ "5 tweet mới nhất (không có account) → `clarify(text)`", chạy base 3 lần để đo độ dao động. Sau đó xử lý G10 (gọi lặp `lookup`) và E06 ("X nhưng kiểm tra Y trước" → gọi cả hai tool); thêm rule "không đề nghị gửi khi chưa có nội dung từ tool chạy thành công".

## 8. Tài liệu tham khảo

- [README.md](../../README.md), [RUBRIC.md](../../RUBRIC.md), [SUBMISSION.md](../../SUBMISSION.md), [docs/TOOL-SETUP.md](../../docs/TOOL-SETUP.md)
- Wikipedia REST API, Hacker News Algolia API, GitHub REST `search/repositories`, Hugging Face Hub `api/models`, Tavily, Firecrawl, RapidAPI Twitter API45, Telegram Bot API.
