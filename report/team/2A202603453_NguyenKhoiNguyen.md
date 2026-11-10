# Báo cáo cá nhân — Nguyễn Khôi Nguyên — 2A202603453

## 1. Thông tin thành viên

- **Họ tên:** Nguyễn Khôi Nguyên
- **MSSV:** 2A202603453
- **Email:** _(điền)_
- **GitHub:** [nguyenkhoinguyen07122005-cpu](https://github.com/nguyenkhoinguyen07122005-cpu)

## 2. Phần việc phụ trách

| Gói | Mục tiêu | Phạm vi |
|---|---|---|
| P0 | Baseline v0 và công cụ phân tích cho cả nhóm | Chạy eval v0, snapshot prompt/tools v0, dòng v0 trong version log, script ghi log và so sánh run |
| P7b | Báo cáo nhóm | Tổng hợp `report/team/group_report.md` (Phần A + B) từ run JSON, version log, transcript |
| Phối hợp | Chia gói việc và tích hợp | Đề xuất cách chia P0–P8 và thứ tự merge, chuẩn bị nhánh `team-kit` cho các thành viên lấy file |

## 3. Đóng góp cụ thể

- **Baseline v0:** chạy 20 case base bằng OpenRouter `openai/gpt-4o-mini` → **0.70 (14/20)**, không có lỗi provider. Đọc `failures`/`actual_tool_calls` và xác định cả 6 case FAIL (R08, R10, R11, R12, R13, R14) đều xuất phát từ 3 chỉ dẫn xấu trong prompt starter ("pick one tool", "đừng hỏi, cứ đoán", "cứ gửi") → nhóm chọn hướng *mỗi version gỡ đúng một chỉ dẫn* (v1–v3), rồi mới sửa `tools.yaml` (v4).
- **Công cụ dùng chung:** `scripts/log_version.py` (ghi một dòng version log từ run JSON, hash và metric lấy tự động, `metric_before` nối tiếp) và `scripts/compare_runs.py` (ma trận PASS/FAIL, nhóm lỗi, hướng sửa xếp theo tác động). Các thành viên dùng `log_version.py` để ghi v1–v5.
- **Báo cáo nhóm:** điền toàn bộ A1–A3, B1–B7, mục 3, 5, 7 trong `group_report.md` dựa trên run trên `main`; ghi rõ phát hiện chính là **bước tăng lớn nhất (0.80 → 0.95) đến từ `tools.yaml` v4**, không phải từ prompt, và các điểm còn lại (G10, E06, run Ollama không hợp lệ, bonus chưa đạt).
- **Bằng chứng chat live:** chạy `scripts/run_chat_demo.py` với cấu hình v5 (6 lượt: yêu cầu thường → thiếu thông tin rồi bổ sung → yêu cầu đăng Telegram có xác nhận → tool mới), dùng làm bằng chứng B4.
- **Thử nghiệm không đưa vào bài nộp:** đã chạy lại v1–v5 trên cùng provider OpenRouter để số liệu đồng nhất (v1 0.80, v2 0.80, v3 0.80, v4 0.95, v5 0.95) và mở PR tích hợp lớn (Final). Nhóm quyết định giữ kết quả do từng thành viên tự chạy nên PR được revert; kết quả lần chạy lại chỉ dùng để đối chiếu xu hướng (cùng kết luận v4 là bước cải thiện lớn nhất).

## 4. Bằng chứng

- File/commit/PR:
  - [runs/v0_B_base_openrouter_20261110T104242979050.json](../../starter_v0/runs/v0_B_base_openrouter_20261110T104242979050.json), [versions/v0](../../starter_v0/artifacts/versions/v0/), dòng v0 trong [version_log.csv](../../starter_v0/artifacts/version_log.csv)
  - [analysis/v0_comparison.md](../../starter_v0/analysis/v0_comparison.md), [scripts/log_version.py](../../starter_v0/scripts/log_version.py), [scripts/compare_runs.py](../../starter_v0/scripts/compare_runs.py)
  - [PR #1 — v0 baseline](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval/pull/1)
  - [transcripts/v5_openrouter_20261110T165629438183.transcript.json](../../starter_v0/transcripts/v5_openrouter_20261110T165629438183.transcript.json)
  - [report/team/group_report.md](group_report.md)
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Dùng trợ lý AI (Claude) để gợi ý prompt/tool declaration, code script, unit test, cách chia việc và thao tác git.
  - Tự kiểm tra: chạy `pytest` (124 passed, 0 skipped trên `main`); chạy eval thật bằng key của mình và đọc `summary`, `failures`, `observed_mismatch`, `actual_tool_calls` trong run JSON; chỉ dùng run có `provider_error_cases = 0`; mọi số liệu trong báo cáo đối chiếu lại với run JSON và version log, không ghi theo cảm giác; chat thử trên UI và đọc transcript.

## 5. Tự đánh giá

- **Làm tốt:** chốt hướng tối ưu từ log v0 thay vì đoán; cung cấp công cụ để cả nhóm ghi version log nhất quán; báo cáo nhóm trỏ được tới file thật và ghi trung thực các phần chưa đạt.
- **Chưa tốt:** PR tích hợp lớn ghi đè kết quả của thành viên khác nên phải revert — lẽ ra cần thống nhất với nhóm trước; báo cáo nhóm hoàn thiện sát deadline; chưa sửa được R10/G10/E06.
- **Lần sau:** đo trước rồi mới đặt giả thuyết; khi lỗi là `wrong_arg_value` thì ưu tiên sửa parameter description; thống nhất quy trình merge trước khi chạy lại kết quả của người khác.
