# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: 1 trang, xong trước 16:30. Bản poster: `artifacts/poster.html`.
> - **PHẦN B — Chi tiết / Bằng chứng**: dựa trên log thật. Các khối nằm giữa `<!-- AUTO:... -->` được
>   `python scripts/fill_report.py` điền **tự động từ `runs/*.json`, `version_log.csv`, `transcripts/`** — không gõ tay số liệu.

## Team

- Team: _(điền tên nhóm)_
- Members: _(điền họ tên + MSSV)_
- Provider/model: OpenRouter — `openai/gpt-4o-mini` (mặc định của `providers/openrouter_provider.py`)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

**Research agent cho tin tức công nghệ/AI**: tìm tin trên web, đọc tweet của một người hoặc theo chủ đề, đọc nội dung một URL, tìm paper arXiv, tra Wikipedia, xem Hacker News, tìm repo GitHub và model Hugging Face, tra quy định nội bộ công ty, rồi gom thành bản tin. Agent **hỏi lại khi thiếu thông tin** (không đoán account/URL) và **luôn xin xác nhận trước khi đăng lên Telegram**.

**Link dùng thử (deploy):**

> Chạy `streamlit run app.py` rồi `cloudflared tunnel --url http://localhost:8501`.
>
> URL: _(dán link `https://<random>.trycloudflare.com` khi demo)_

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu account/URL/chủ đề, hoặc hỏi Có/Không trước khi gửi | không |
| timeline | Lấy tweet mới nhất **của một người** (tự đổi tên → handle: Sam Altman → `sama`) | không |
| social_search | Tìm tweet **về một chủ đề** (`Latest` / `Top`) | không |
| lookup | Tìm tin/thông tin trên web (Tavily, `topic=news`, `timeframe=day/week/...`) | không |
| fetch | Đọc và tóm tắt nội dung một URL (Firecrawl) | không |
| format | Gom các item đã có thành bản tin markdown | không |
| send | Đăng lên Telegram — **chỉ khi đã xác nhận** (`confirmed=true`) | không (bonus) |
| policy | Tra company policy nội bộ (nguồn trích dẫn, bảo mật dữ liệu, đăng bài...) | không (bonus) |
| papers / paper_text | Tìm paper arXiv / tải PDF arXiv và trích text | không (bonus) |
| **wikipedia** | Tra kiến thức nền: một người, khái niệm, tổ chức là gì (en/vi) | **có** |
| **hackernews** | Xem dân dev trên Hacker News bàn gì (top/latest, theo khoảng thời gian) | **có** |
| **github_repos** | Tìm repo mã nguồn mở trên GitHub (lọc ngôn ngữ, sắp theo sao) | **có** |
| **hf_models** | Tìm model trên Hugging Face theo task (text-to-image, ASR...) và độ phổ biến | **có** |

## A3. Câu hỏi mẫu để thử

1. `Tin tức AI hôm nay có gì nổi bật?` → `lookup(topic=news, timeframe=day)`
2. `Tóm tắt 5 tweet mới nhất giúp mình` → agent hỏi lại *"của ai?"* → trả lời `Của Andrej Karpathy` → `timeline(karpathy, 5)`
3. `Tóm tắt bài này: https://www.anthropic.com/research` → `fetch`
4. `Tuần này trên Hacker News dân dev bàn gì về Rust?` / `Tìm 5 repo GitHub nhiều sao nhất về LLM agent framework`
5. `Đăng bản tin AI hôm nay lên Telegram` → agent **hỏi xác nhận Có/Không** trước, chỉ gửi sau khi bấm "Có"

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Mỗi version đổi **một** giả thuyết. Snapshot đầy đủ của từng version nằm ở `artifacts/versions/vN/{system_prompt.md,tools.yaml}`
(bản cuối `v4` = `artifacts/system_prompt.md` + `artifacts/tools.yaml`), nên mọi run có thể chạy lại và hash khớp `version_log.csv`.

| Version | Thay đổi | Giả thuyết (viết trước khi chạy) |
|---|---|---|
| v0 | baseline starter | Prompt cố ý xấu (đoán thay vì hỏi, tự gửi, ép một tool) + description mơ hồ → FAIL ở clarify/confirm/parallel/args |
| v1 | `system_prompt.md` | Bỏ 3 chỉ dẫn xấu + 4 rule boundary → sửa R10, R11, R12, R13 (và giữ R08, R09, R14 không gọi tool) mà **chưa** đổi tools.yaml |
| v2 | `tools.yaml` | Description "làm gì / khi nào dùng / khi nào KHÔNG dùng" + convention args (handle không `@`, map tên→handle, `topic=news`, `timeframe`, `search_type=Top`, `query` chỉ là keyword) → sửa các `wrong_arg_value` |
| v3 | `system_prompt.md` | Bảng routing + rule multi-turn (chỉ trả lời lượt cuối, carry-over, correction ghi đè) → tăng `multiturn_accuracy` (M01–M06) |
| v4 | `tools.yaml` + `system_prompt.md` | Thêm 4 tool mới có ranh giới khi-nào-KHÔNG-dùng → **không regression** trên base, đồng thời PASS group eval |

Kết quả thật (tự sinh):

<!-- AUTO:B1 -->
_Chưa có run base nào — chạy `python scripts/run_all.py`._
<!-- /AUTO:B1 -->

Ma trận PASS/FAIL từng case qua các version:

<!-- AUTO:B1_MATRIX -->
_Chưa có run._
<!-- /AUTO:B1_MATRIX -->

## B2. Failure Analysis

Mỗi case FAIL lần đầu xuất hiện ở version nào, model đã gọi gì, và version nào sửa được (tự sinh từ `results[*].result`):

<!-- AUTO:B2 -->
_Chưa có run._
<!-- /AUTO:B2 -->

Cơ chế lỗi và cách sửa tương ứng (phân tích từ prompt/tool declaration của starter — đối chiếu với bảng trên sau khi chạy):

| Nhóm case | Loại lỗi | Nguyên nhân gốc trong starter | Fix (version) |
|---|---|---|---|
| R10, R11 | missing_info | Prompt ra lệnh *"đừng hỏi lại, đoán luôn… chọn Sam Altman, đoán URL"* | Rule 1: thiếu account/URL → `clarify(text)` (v1) |
| R12 | wrong_boundary | Prompt: *"muốn gửi thì cứ gửi"*; `send` mô tả "Gửi một đoạn văn bản đi" | Rule 2 + description `send` chỉ khi `confirmed=true` (v1, v2) |
| R13 | wrong_tool (thiếu call) | Prompt: *"Always … single step. Pick one tool"* | Rule 4: hai nguồn → hai tool trong cùng response (v1) |
| R01, R05, M01, M03, M05 | wrong_arg_value | Không có convention handle (`Sam Altman` → `sama`) | Map tên→handle trong param `screenname` (v2) |
| R03, R06, R13, M02 | wrong_arg_value | `topic`/`timeframe` không mô tả; query bị nhồi "tin tức hôm nay" | `query` chỉ keyword, `news`/`day`/`week` trong description (v2) |
| R07 | wrong_arg_value | `search_type` chỉ ghi "Cách sắp xếp" | "phổ biến/top" → `Top` (v2) |
| M01–M06 | wrong_arg_value / wrong_tool | Không có rule lượt cuối + carry-over + correction | Section *Multi-turn conversations* (v3) |

## B3. Team Eval Cases

10 case trong `data/eval_group.json` (5 single turn + 5 multi turn), 4 tool mới đều có case route tới:

| Case ID | Turns | What It Tests | Expected Tool/Behavior |
|---|---|---|---|
| G01_wikipedia_vi_concept | single | Hỏi khái niệm + Wikipedia tiếng Việt | `wikipedia(lang=vi)` |
| G02_hackernews_top_week | single | HN thay vì Twitter; tuần này + nhiều điểm | `hackernews(query=Rust, sort=top, timeframe=week)` |
| G03_github_top_stars | single | Tìm repo, "5 repo", "nhiều sao nhất" | `github_repos(sort=stars, limit=5)` |
| G04_hf_models_task | single | Model HF theo task, "tải nhiều nhất" | `hf_models(task=text-to-image, sort=downloads)` |
| G05_arxiv_newest_sort | single | "paper mới nhất" | `papers(sort_by=submittedDate)` |
| G06_multiturn_github_fill_language | multi | Carry chủ đề + thêm filter ngôn ngữ + sort | `github_repos(language=Rust, sort=stars)` |
| G07_multiturn_send_after_yes | multi | Sau khi hỏi xác nhận, user nói "Có" | `send(text=…, confirmed=true)` |
| G08_multiturn_twitter_to_hn | multi | Bỏ Twitter → HN, giữ chủ đề, "mới nhất" | `hackernews(query=Claude, sort=latest)` |
| G09_multiturn_wiki_correction | multi | Sửa người + chọn bản tiếng Anh | `wikipedia(query=Geoffrey Hinton, lang=en)` |
| G10_multiturn_cancel_send | multi | User huỷ đăng, đổi sang tìm web | `lookup(topic=news, timeframe=week)`, **không** `send` |

Kết quả thật (tự sinh):

<!-- AUTO:B3 -->
_Chưa có run suite `group`._
<!-- /AUTO:B3 -->

Extension eval (policy + arXiv) trên bản cuối:

<!-- AUTO:B3_EXT -->
_Chưa có run suite `extension`._
<!-- /AUTO:B3_EXT -->

## B4. Live Chat Evidence

`scripts/run_chat_demo.py` chạy đúng vòng lặp tool của `chat.py` với 6 lượt: tin AI hôm nay → thiếu account → bổ sung account → yêu cầu đăng Telegram (phải hỏi Có/Không) → "Có" → câu dùng tool mới. UI Streamlit cũng ghi transcript cùng format (`transcripts/ui_*.transcript.json`).

<!-- AUTO:B4 -->
_Chưa có transcript — chạy `python scripts/run_chat_demo.py ...` hoặc `python chat.py ...`._
<!-- /AUTO:B4 -->

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `tools/send/tool.py`, case R12 + G07 + G10, transcript lượt 4–5 | Chỉ gửi khi `confirmed` là boolean `true`; nếu chưa xác nhận tool trả `awaiting_user` để chat/UI dừng lại hỏi Có/Không | Sửa BUG-1 (`confirmed="false"` vẫn gửi), BUG-2 (token lộ trong error), retry plain text khi Markdown lỗi |
| arXiv/company policy | `data/eval_research_extension.json`, run suite `extension` | `policy_area` mô tả rõ từng nhóm; `papers` vs `paper_text` tách rõ tìm vs đọc | Policy trả `untrusted_text` riêng cho dòng giống lệnh (prompt injection trong KB) — có test |
| UI | `app.py` (Streamlit) | Chat nhiều lượt, xem từng tool call/result, nút ✅/❌ khi agent chờ xác nhận gửi, sidebar chọn provider/model/version, ghi transcript | Không lưu key trong UI; lỗi provider hiển thị thay vì crash |
| 4 tool mới (> 3 → bonus point) | `tools/{wikipedia,hackernews,github_repos,hf_models}/` + `TOOL.md` + `tools/__init__.py` + `tools.yaml` | API công khai, **không cần key**; trả item cùng schema (`title,url,source,summary`) nên `format` dùng lại được | Clamp `limit`, enum sai → mặc định, query rỗng → error dict không gọi mạng; `GITHUB_TOKEN` (tuỳ chọn) không bao giờ trả về trong result |
| Tool unit tests (`tests/`) | `analysis/pytest_before_fix.txt`, `analysis/pytest_after_fix.txt` | **124 passed, 0 failed, 0 skipped** | Toàn bộ offline (`fake_http`), không tốn credit |

**Tool unit tests:** `tests/test_tools_todo.py` có 42 test: 14 stub TODO đã điền, 15 test cho 4 tool mới (≥ 3/tool: happy path, input xấu từ model, nhánh lỗi), và **13 regression test cho 12 bug tìm được trong tool có sẵn**. Cả 13 test này FAIL trên code starter (`analysis/pytest_before_fix.txt`: `13 failed, 111 passed`) và PASS sau khi sửa.

| Bug | Tool | Input biên từ model | Hành vi sai của starter | Fix |
|---|---|---|---|---|
| BUG-1 | send | `confirmed="false"` | Chuỗi khác rỗng là truthy → **vẫn đăng lên Telegram** | Chỉ chấp nhận `True` hoặc `"true"` |
| BUG-1b | send | `confirmed=false` trong chat | Không có `awaiting_user` → `chat.py` lặp tool tới `max_tool_rounds` | Trả `awaiting_user` + câu hỏi Có/Không kèm nội dung |
| BUG-2 | send | token sai / HTTP 401 | Message của `HTTPError` chứa URL `bot<TOKEN>` → **token lộ vào transcript** | Redact token |
| BUG-3 | send | text có `*`/`_` lẻ | Telegram 400 "can't parse entities" → không gửi được | Retry không `parse_mode` |
| BUG-4 | timeline | `screenname="@sama"` | Gọi API với `@sama` → không có kết quả | Bỏ `@` và khoảng trắng |
| BUG-5 | timeline, social_search | `limit=-1`, `limit=0` | `items[:-1]` bỏ mất tweet cuối; `0` → 5 | `clamp_int(limit, 5, 1, 50)` |
| BUG-6 | social_search | `search_type="top"` | Gửi nguyên chữ thường, API cần `Top` | Chuẩn hoá về `Top`/`Latest` |
| BUG-7 | lookup | `max_results=50`, `timeframe="today"`, `topic="News"` | Gửi thẳng → Tavily trả lỗi | Clamp 1–20, alias timeframe, chuẩn hoá topic |
| BUG-8 | fetch | `url=""` | Vẫn gọi Firecrawl (tốn credit) | Trả error dict trước khi gọi mạng |
| BUG-9 | fetch | `url="openai.com/research"` | Firecrawl từ chối URL thiếu scheme | Thêm `https://` |
| BUG-10 | format | `items=["headline 1", ...]` | `AttributeError` → tool crash | Chuỗi → `{"title": ...}` |
| BUG-11 | format | item không có url | Dòng kết thúc bằng `" - "` lơ lửng | Bỏ separator khi không có nguồn |
| BUG-12 | clarify | `response_type="free"` | UI không biết render kiểu gì | Fallback `text`; `yes_no` có sẵn options |

**Ví dụ lỗi unit test bắt được mà eval không bắt được:** BUG-1. Eval chỉ so `tool_calls` + args: nếu model gọi `send(text=..., confirmed="false")`, eval báo `wrong_arg_value` nhưng tool **vẫn đăng bài thật** — side effect đã xảy ra. Tương tự BUG-2: G07 có thể PASS hoàn toàn (đúng tool, đúng `confirmed=true`), nhưng nếu token sai thì `tool_results` trong run JSON/transcript chứa nguyên bot token — eval không bao giờ nhìn tới chỗ đó.

## B6. Reflection

- **Fix thuộc `system_prompt.md`:** những gì là *chính sách hành vi* áp dụng cho mọi tool — khi nào hỏi lại thay vì đoán, ranh giới hành động ghi (xác nhận trước khi gửi), câu ngoài phạm vi/không cần tool, được gọi nhiều tool song song, và cách đọc hội thoại nhiều lượt (lượt cuối, carry-over, correction). Starter đặt 3 chỉ dẫn xấu đúng ở đây nên chỉ sửa tools.yaml là không đủ.
- **Fix thuộc `tools.yaml`:** những gì gắn với *một tool cụ thể* — tool làm gì, khi nào dùng / khi nào KHÔNG dùng (để phân biệt timeline vs social_search, lookup vs fetch, tool mới vs tool cũ), và convention từng tham số (handle không `@`, map tên→handle, `topic`, `timeframe`, `search_type`, `query` chỉ là keyword, URL giữ nguyên). Model đọc description ngay lúc điền args nên đặt convention ở đây hiệu quả và không làm prompt dài thêm.
- **Cần review thủ công thay vì chấm tự động:** (1) case `no_tool` (R08, R09, R14) — eval chỉ kiểm tra *không gọi tool*, không kiểm tra câu trả lời có từ chối lịch sự/đúng không; (2) chất lượng câu hỏi `clarify` (có hỏi đúng thứ bị thiếu không) — eval chỉ xem `response_type`; (3) nội dung `send(text=...)` có đúng bản tin đã được xác nhận; (4) `query` tự do của `social_search`/`papers`/`github_repos` khi expected args để `{}`; (5) tool trả lỗi (thiếu key, 429) nhưng eval vẫn PASS vì chỉ chấm routing — phải đọc `tool_results` trong run JSON.
- **Cải thiện tiếp:** chấm cả `tool_results` (case FAIL nếu tool trả `error`); thêm case `clarify` kiểu `choice`; đưa map tên→handle thành tool `resolve_handle` (tra cứu thật) thay vì liệt kê trong description; chạy mỗi version ≥ 3 lần để đo độ dao động khi `temperature=0` nhưng provider vẫn không xác định; thêm eval chống prompt-injection từ kết quả `fetch`/`policy`.

## B7. Small Local Model Challenge (bonus)

Chuẩn bị sẵn 2 vòng tối ưu cho model nhỏ (không phá bản cloud):

- `artifacts/local/v4-local/` — giả thuyết: *model nhỏ bị lạc vì prompt dài + 14 tool*. Prompt 5 rule ngắn; chỉ giữ 6 tool base eval cần; mỗi description 1 câu kèm **ví dụ args**; bỏ field optional (`options`, `max_results`, `limit` của social_search).
- `artifacts/local/v5-local/` — giả thuyết: *few-shot cụ thể giúp model nhỏ gọi `clarify` và điền args đúng hơn*. Thêm 9 ví dụ routing (dùng người/chủ đề **khác** case eval để không học thuộc đáp án).
- Lệnh: `python scripts/run_all.py --skip-base --skip-group --skip-extension --skip-chat --local-models qwen2.5:7b llama3.2:3b` → chạy `v4-<model>` (prompt cloud), `v4-local-<model>`, `v5-local-<model>` cho từng model rồi kiểm tra ngược `v5-local-on-cloud`.

<!-- AUTO:B7 -->
_Chưa chạy local model — `python scripts/run_all.py --skip-base --skip-group --skip-extension --skip-chat --local-models qwen2.5:7b llama3.2:3b`._
<!-- /AUTO:B7 -->

Lỗi đặc thù của model nhỏ (đếm tự động từ run JSON):

<!-- AUTO:B7_PATTERNS -->
_Chưa có run local._
<!-- /AUTO:B7_PATTERNS -->

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng? _(so cột case_accuracy v4-local vs v5-local ở bảng trên)_
- Bản prompt tối ưu cho local chạy trên model cloud thì sao? _(dòng `v5-local-on-cloud` trong `version_log.csv`)_
- Khi nào chọn model local thay vì cloud? Khi dữ liệu không được rời máy (policy `data_privacy`), khi cần chạy offline/miễn phí cho các tác vụ routing đơn giản; giữ cloud cho multi-turn và câu cần nhiều tool song song.
