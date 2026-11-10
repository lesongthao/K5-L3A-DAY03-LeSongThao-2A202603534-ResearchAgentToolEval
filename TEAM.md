# TEAM — Day 03 Research Agent Tool Eval

## Thông tin nhóm

- **Tên nhóm:** Chưa chốt tên nhóm.
- **Lớp:** K5 — L3A.
- **Repo nhóm:** [K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval).
- **Nhánh nộp:** `main`.
- **Commit chốt bài nộp:** Chưa chốt; ghi sau khi hoàn thiện báo cáo nhóm và bằng chứng demo.
- **Provider/model:** v0–v1 dùng OpenRouter / `openai/gpt-4o-mini`; v2–v5 dùng OpenAI trực tiếp / `gpt-4o-mini`. Chi tiết trong [version log](starter_v0/artifacts/version_log.csv).

## Thành viên và phân công

| STT | Họ tên | MSSV | GitHub | Gói phụ trách |
|---:|---|---|---|---|
| 1 | Nguyễn Khôi Nguyên | 2A202603453 | [nguyenkhoinguyen07122005-cpu](https://github.com/nguyenkhoinguyen07122005-cpu) | P0, P7b |
| 2 | Lê Sông Thao | 2A202603534 | [lesongthao](https://github.com/lesongthao) | P1, P5 |
| 3 | Bùi Xuân Thành | 2A202603521 | [KDAGRAGAS](https://github.com/KDAGRAGAS) | P2, P6a |
| 4 | Trần Đăng Khoa | 2A202603364 | [khoatran134563-2k3](https://github.com/khoatran134563-2k3) | P3, P4, P6b |
| 5 | Quang Bảo — cần xác nhận họ tên đầy đủ | Chưa xác nhận | [wadiobao](https://github.com/wadiobao) | P7a, P8 (bonus) |

Thông tin chưa xác nhận cần được thành viên bổ sung trước khi chốt bài nộp. Mỗi thành viên tự nộp cùng link repo nhóm trên LMS theo [SUBMISSION.md](SUBMISSION.md).

## Đóng góp và bằng chứng

### Nguyễn Khôi Nguyên — P0, P7b

- **P0:** Baseline v0, snapshot, version log và công cụ phân tích; base đạt 14/20 (70%). Bằng chứng: [run v0](starter_v0/runs/v0_B_base_openrouter_20261110T104242979050.json), [phân tích v0](starter_v0/analysis/v0_comparison.md), [PR #1](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval/pull/1).
- **P7b:** Phụ trách tổng hợp [báo cáo nhóm](report/team/group_report.md); báo cáo hiện còn cần hoàn thiện.
- **Báo cáo cá nhân:** Chưa có file trong `report/team/` tại thời điểm rà soát.

### Lê Sông Thao — P1, P5

- **P1:** Cho phép trả lời không dùng tool khi phù hợp và gọi nhiều tool khi yêu cầu nhiều nguồn; base tăng từ 14/20 lên 15/20 (70% → 75%). Bằng chứng: [nhận xét v1](starter_v0/analysis/notes_v1.md), [run v1](starter_v0/runs/v1_B_base_openrouter_20261110T145322191182.json), [commit P1](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval/commit/d47ed38fd918502eaad88ef979fa048a2f494b14).
- **P5:** Tích hợp test và sửa 12 lỗi của tool có sẵn; trước sửa 13 failed / 76 passed, sau sửa 89 passed / 0 skipped. Bằng chứng: [log trước sửa](starter_v0/analysis/pytest_before_fix.txt), [log sau sửa](starter_v0/analysis/pytest_after_fix.txt), [PR #9](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval/pull/9).
- **Báo cáo cá nhân:** [2A202603534_LeSongThao.md](report/team/2A202603534_LeSongThao.md).

### Thành — P2, P6a

- **P2:** Thêm quy tắc hỏi lại khi thiếu tài khoản hoặc URL; base đạt 16/20 (80%). R10/R11 đã hỏi lại nhưng vẫn thiếu tham số `response_type` trong lượt v2. Bằng chứng: [nhận xét v2](starter_v0/analysis/notes_v2.md), [PR #11](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval/pull/11).
- **P6a:** Thêm triển khai và đăng ký Python cho `wikipedia`, `hackernews`, `github_repos`, `hf_models`, cùng 15 unit test. Bằng chứng: [registry](starter_v0/tools/__init__.py), [test](starter_v0/tests/test_tools_todo.py), [PR #13](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval/pull/13).
- **Báo cáo cá nhân:** Chưa có file trong `report/team/` tại thời điểm rà soát.

### Trần Đăng Khoa — P3, P4, P6b

- **P3:** Tích hợp quy tắc xác nhận trước khi gửi; base v3 đạt 16/20 (80%). Bằng chứng: [nhận xét v3](starter_v0/analysis/notes_v3.md), [PR #15](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval/pull/15).
- **P4:** Làm rõ mô tả và tham số công cụ; base v4 đạt 19/20 (95%). Bằng chứng: [nhận xét v4](starter_v0/analysis/notes_v4.md), [PR #17](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval/pull/17).
- **P6b:** Tích hợp khai báo bốn tool mới và 10 case nhóm; v5 base 20/20, group 9/10, extension 9/10. Bằng chứng: [nhận xét v5](starter_v0/analysis/notes_v5.md), [eval nhóm](starter_v0/data/eval_group.json), [PR #19](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval/pull/19).
- **Báo cáo cá nhân:** [2A202603364_TranDangKhoa.md](report/team/2A202603364_TranDangKhoa.md).

### Quang Bảo — P7a, P8 (bonus)

- **P7a:** Tích hợp UI Streamlit, dependency, script demo và poster. Bằng chứng: [app.py](starter_v0/app.py), [script demo](starter_v0/scripts/run_chat_demo.py), [poster](starter_v0/artifacts/poster.html), [PR #12](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval/pull/12).
- **Demo còn cần bổ sung:** Transcript hiện có mang nhãn v5 nhưng hash khớp prompt v1; cần chạy lại bằng cấu hình v5 hiện tại, đủ yêu cầu thường, thiếu thông tin rồi bổ sung và yêu cầu gửi/đăng. Cần ghi lệnh chạy UI và link dùng thử vào mục A1 của báo cáo nhóm.
- **P8:** Bonus model local; chưa có run Ollama trên `main` tại thời điểm rà soát, chưa tính là hoàn thành.
- **Báo cáo cá nhân:** Chưa có file trong `report/team/` tại thời điểm rà soát.

## Cách đối chiếu đóng góp

- Phân biệt gói được giao với phần đã có bằng chứng; các mục còn thiếu được ghi rõ ở trên.
- Các báo cáo cá nhân mô tả phạm vi tích hợp, kiểm chứng, nguồn mã dùng chung và công cụ hỗ trợ của từng thành viên theo [RULES.md](RULES.md).
- Kết quả eval đo lời gọi tool và tham số; không tự chứng minh API tool thực thi thành công. Chưa có bằng chứng gửi Telegram thành công trong lượt group v5.
- Trạng thái trong file này được đối chiếu với `main` tại commit `3e67cc5` ngày 10/11/2026 (GMT+7); cập nhật cùng các PR hoàn thiện tiếp theo.
