# Báo cáo cá nhân — Bùi Xuân Thành — 2A202603521

## 1. Thông tin thành viên

- **Họ tên:** Bùi Xuân Thành.
- **MSSV:** 2A202603521.
- **Email:** _(điền nếu muốn)_.
- **GitHub:** [KDAGRAGAS](https://github.com/KDAGRAGAS) — tên tác giả trong commit: `buithanh`.
- **Phần việc phụ trách:** P2 và P6a.

## 2. Phần việc phụ trách

| Gói | Mục tiêu | Phạm vi |
|---|---|---|
| P2 | Agent hỏi lại thay vì tự đoán khi thiếu tài khoản hoặc URL | Snapshot prompt v2, chạy base eval, ghi version log, phân tích R10/R11 (mục tiêu) và R13/M06 (theo dõi) trong `notes_v2.md` |
| P6a | Bổ sung 4 tool tra cứu mới cho research agent | Code và `TOOL.md` của `wikipedia`, `hackernews`, `github_repos`, `hf_models`; đăng ký trong `tools/__init__.py`; 15 unit test offline nối vào `tests/test_tools_todo.py` |

Snapshot prompt v2 và code/test của bốn tool lấy từ nhánh dùng chung `team-kit` do Nguyễn Khôi Nguyên chuẩn bị (commit `d2b2752`). Phạm vi của tôi là tích hợp đúng thứ tự vào `main`, kiểm chứng (diff, eval, pytest), phân tích kết quả và ghi lại bằng chứng.

## 3. Đóng góp cụ thể

### P2 — Prompt v2: hỏi lại thay vì đoán

Thay đúng **một đoạn** so với v1: bỏ chỉ dẫn *"The user is busy and hates being asked questions… just make a sensible guess… pick a well-known account like Sam Altman… assume a likely URL"* và thay bằng quy tắc: khi thiếu tài khoản (không nêu tweet của ai) hoặc thiếu URL thì không đoán, gọi `clarify` với `response_type="text"` và chỉ hỏi phần còn thiếu. Hai quy tắc của P1 và `tools.yaml` của v1 được giữ nguyên (kiểm tra bằng `git diff --no-index` giữa `versions/v1/` và `versions/v2/`); câu "cứ gửi" để lại cho P3.

**Giả thuyết:** R10_missing_handle và R11_missing_url hết lỗi đoán thay vì hỏi lại; R13 và M06 không bị regression.

Chạy 20 case base với model `gpt-4o-mini` qua **OpenAI API trực tiếp** (`--provider openai`); v0/v1 chạy qua OpenRouter (`openai/gpt-4o-mini`), cùng model.

| Chỉ số | v1 | v2 |
|---|---:|---:|
| Case PASS | 15/20 | 16/20 |
| Case accuracy | 0.75 | 0.80 |
| Tool routing accuracy | 0.80 | 0.90 |
| Argument accuracy | 0.75 | 0.80 |
| Multi-turn accuracy | 0.83 | 0.83 |
| Lỗi provider | 0 | 0 |

| Case | v1 | v2 | Nhận xét |
|---|---|---|---|
| R10 | FAIL — gọi `timeline(screenname="sama")` | FAIL — gọi `clarify("Bạn muốn tóm tắt tweet của tài khoản nào?")` nhưng thiếu `response_type` | Đã hết đoán, hỏi đúng phần thiếu |
| R11 | FAIL — gọi `fetch(url="https://www.example.com/article")` | FAIL — gọi `clarify` xin URL nhưng thiếu `response_type` | Như R10 |
| R13 | FAIL — `lookup` sai `query`, thiếu `topic` | PASS | Prompt v2 không đụng convention tham số, nhiều khả năng là dao động giữa các lần chạy/provider |
| M06 | FAIL — gọi thừa `social_search` | FAIL — giống v1 | Không phải regression mới |
| R12 | FAIL | FAIL | Đúng dự kiến, thuộc P3 |

**Kết luận:** giả thuyết **đúng một phần**. Bỏ chỉ dẫn "cứ đoán" đã sửa được hành vi (đoán → hỏi lại), nhưng model chưa điền `response_type="text"` dù prompt đã ghi rõ. Nguyên nhân nằm ở khai báo tool: trong `tools.yaml`, `clarify.response_type` có `default: "text"` và không nằm trong `required`, nên model coi là tuỳ chọn. Tôi không sửa thêm prompt trong P2 để giữ mỗi version một giả thuyết, và bàn giao điểm này cho P4 (`tools.yaml`). Mức tăng 0.75 → 0.80 đến từ R13 chứ không đến từ case mục tiêu; điều này được ghi rõ trong `notes_v2.md` để không quy công sai cho thay đổi của v2.

**Theo dõi sau bàn giao:** trên `main`, R11 PASS từ v4 (viết lại `tools.yaml`), và cả R10/R11 PASS ở v5 (base 20/20).

**Ghi chú hash:** `tools_hash` của v2 (`5b22a2476d41`) khác v1 (`8db0ba629f52`) chỉ vì Git trên Windows đổi xuống dòng LF → CRLF khi checkout; nội dung `tools.yaml` giống hệt v1.

### P6a — Bốn tool mới và 15 unit test

| Tool (hàm) | Nguồn dữ liệu | Dùng khi | Xử lý input |
|---|---|---|---|
| `wikipedia` (`wiki_search`) | Wikipedia REST API, không cần key | Kiến thức nền: ai là ai, khái niệm, lịch sử | Tìm trang rồi lấy tóm tắt của kết quả đầu; `lang` sai → `en`; `limit` 1–10; `query` rỗng → error dict, không gọi mạng; gửi `User-Agent` theo yêu cầu Wikimedia |
| `hackernews` (`hn_search`) | Hacker News Algolia API, không cần key | Người dùng hỏi về Hacker News | `sort` `top`/`latest` → `/search` hoặc `/search_by_date`; `timeframe` → `numericFilters`; giữ cả `url` bài và `discussion_url`; `limit` 1–30 |
| `github_repos` (`github_search`) | GitHub REST `search/repositories`; `GITHUB_TOKEN` tuỳ chọn | Tìm repo/thư viện mã nguồn mở | `language`, `created_within` → qualifier; `sort` `stars`/`updated`/`best_match`; token chỉ gửi trong header, không bao giờ trả về; `limit` 1–20 |
| `hf_models` (`hf_model_search`) | Hugging Face Hub API, không cần key | Tìm model/checkpoint mở | `task` → `pipeline_tag`; `sort` `downloads`/`likes`/`trending`/`recent`; cần `query` hoặc `task`; `limit` 1–20 |

Mỗi tool có `TOOL.md` mô tả khi nào dùng / không dùng và được đăng ký trong `TOOL_FUNCTIONS` (`tools/__init__.py`). P6a làm sau P5 vì 15 test mới được nối vào cuối file test mà P5 đã hoàn thiện; làm trước sẽ bị P5 ghi đè.

| Tool | Số test | Hành vi được kiểm tra |
|---|---:|---|
| `wikipedia` | 4 | Request đúng URL/params và map kết quả + tóm tắt; input xấu từ model; `lang="vi"` dùng domain `vi`; lỗi HTTP → error dict |
| `hackernews` | 4 | `top` + `week` dựng đúng request và map hit; `latest` dùng `search_by_date`, không lọc thời gian; input xấu; lỗi mạng → error dict |
| `github_repos` | 4 | Dựng đúng qualifier và map item; token được gửi nhưng không lộ trong kết quả; input xấu; rate limit → error dict |
| `hf_models` | 3 | Map `task`/`sort` sang tham số Hub; input xấu; lỗi HTTP → error dict |

Các test chạy offline (fixture `fake_http` chặn mạng) và kiểm tra cả request gửi đi lẫn kết quả trả về. Trên commit P6a: `pytest` toàn bộ **104 passed, 0 failed** (89 của P5 + 15 mới); riêng `tests/test_tools_todo.py` 42 passed. Khai báo bốn tool trong `tools.yaml` và eval nhóm thuộc P6b (Trần Đăng Khoa).

## 4. Bằng chứng

### File, commit và PR

| Hạng mục | Bằng chứng |
|---|---|
| Snapshot v2 | [system_prompt.md](../../starter_v0/artifacts/versions/v2/system_prompt.md), [tools.yaml](../../starter_v0/artifacts/versions/v2/tools.yaml) |
| Run P2 / v2 | [v2_B_base_openai_20261110T160703839285.json](../../starter_v0/runs/v2_B_base_openai_20261110T160703839285.json) |
| Run mốc v1 | [v1_B_base_openrouter_20261110T145322191182.json](../../starter_v0/runs/v1_B_base_openrouter_20261110T145322191182.json) |
| Version log và nhận xét | [version_log.csv](../../starter_v0/artifacts/version_log.csv) (dòng v2), [notes_v2.md](../../starter_v0/analysis/notes_v2.md) |
| Bốn tool mới | [wikipedia](../../starter_v0/tools/wikipedia/), [hackernews](../../starter_v0/tools/hackernews/), [github_repos](../../starter_v0/tools/github_repos/), [hf_models](../../starter_v0/tools/hf_models/), [registry](../../starter_v0/tools/__init__.py) |
| Unit test | [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py) — mục 2 "Team-added tools" |
| Commit P2 | [eec06bb — prompt v2: clarify instead of guessing](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval/commit/eec06bb4489c08c24f6231fc2c8dfcc7928f7414), [dcea9f7 — sửa tên tác giả trong version log](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval/commit/dcea9f7c844eb8ed64f3b25615d650d83608b2bc) |
| Commit P6a | [5296089 — feat: 4 new tools + 15 unit tests](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval/commit/52960899131e3292710abbe83e99a889d1d46d61) |
| PR đã được duyệt | [P2 — PR #11](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval/pull/11), [P6a — PR #13](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval/pull/13) |

### AI/công cụ đã dùng và cách kiểm tra kết quả

- **Claude (trợ lý AI):** hỗ trợ đọc repo và `PHAN_CONG.md`, tra cứu lệnh git, so sánh `actual_tool_calls` theo từng case giữa v1 và v2, soạn nháp `notes_v2.md` và báo cáo; rà lại commit đã push và chạy lại pytest trên commit P6a trong môi trường sạch. Eval, version log và thao tác git do tôi tự chạy; mọi số liệu lấy trực tiếp từ run JSON và output lệnh.
- **Git/GitHub:** mỗi gói một nhánh riêng tách từ `origin/main` (`buithanh-p2`, `buithanh-p6a`), chỉ lấy đúng thư mục cần từ `team-kit` bằng `git checkout origin/team-kit -- <path>`; PR do Lê Sông Thao duyệt và merge. Đã loại nhánh nháp `bxt` sau khi phát hiện nó tách từ starter gốc (thiếu P0/P1) và chứa nhầm prompt bản cuối.
- **OpenAI API:** chạy eval v2 với `gpt-4o-mini`; API key chỉ nằm trong `.env` trên máy.
- **pytest:** test offline, chặn mạng bằng `fake_http`.
- **Kiểm chứng:** `git diff --no-index` xác nhận v2 chỉ đổi một đoạn so với v1, `tools.yaml` giữ nguyên; run v2 có `provider_error_cases = 0`, `measured_cases = total_cases = 20`; soát lời gọi tool của R10/R11/R13/M06 thay vì chỉ dựa vào điểm tổng; `log_version.py` tự lấy `metric_before = 0.75` từ dòng v1; sửa placeholder cột tác giả (commit `dcea9f7`); kiểm tra `git status` trước mỗi commit để loại `.env`, `.venv`.

## 5. Tự đánh giá

Qua P2, tôi đã điều chỉnh prompt để agent hỏi lại khi thiếu tài khoản hoặc URL; hành vi đã chuyển từ đoán sang hỏi đúng phần còn thiếu.
Tuy vậy, R10/R11 chưa PASS ở lần chạy v2 vì model vẫn bỏ sót `response_type`, nên tôi cần chú ý cả prompt lẫn khai báo tool.
Ở P6a, tôi tích hợp bốn tool tra cứu và 15 unit test offline; toàn bộ 104 test trên commit đều passed.
Tôi học được cách đọc từng case và lời gọi tool thay vì chỉ nhìn điểm tổng, đồng thời ghi lại bằng chứng rõ ràng khi làm việc qua Git/PR.
Điểm cần cải thiện là phát hiện sớm các giới hạn của schema và kiểm tra giả thuyết eval kỹ hơn trước khi kết luận.
Nếu làm lại, tôi sẽ rà `required`/`default` của tool từ đầu và chuẩn bị checklist đối chiếu từng case mục tiêu.