# Báo cáo cá nhân — Trần Đăng Khoa — 2A202603364

## 1. Thông tin thành viên

- **Họ tên:** Trần Đăng Khoa.
- **MSSV:** 2A202603364.
- **GitHub:** [khoatran134563-2k3](https://github.com/khoatran134563-2k3).
- **Phần việc phụ trách:** P3, P4 và P6b.
- **Provider/model dùng kiểm chứng:** OpenAI trực tiếp, `gpt-4o-mini`.

## 2. Phần việc phụ trách

| Gói | Mục tiêu | Phạm vi |
|---|---|---|
| P3 | Yêu cầu xác nhận trước khi gửi | Tích hợp snapshot v3, chạy base eval, ghi log và phân tích |
| P4 | Làm rõ khai báo tool và quy ước tham số | Tích hợp snapshot v4, cập nhật tools.yaml, chạy test và base eval |
| P6b | Tích hợp khai báo tool mới và eval nhóm | Tích hợp snapshot v5, 10 case nhóm; chạy base, group và extension |

Code và snapshot được lấy từ bộ mã dùng chung do thành viên nhóm chuẩn bị. Đóng góp cá nhân tập trung vào tích hợp đúng phạm vi, tự chạy kiểm chứng bằng API, đọc log, ghi nhận kết quả và đưa thay đổi lên nhánh riêng để nhóm trưởng xem xét merge.

Bốn tool mới và phần triển khai, kiểm thử tương ứng thuộc P6a; tôi phụ trách tích hợp khai báo và đánh giá chúng trong P6b.

## 3. Đóng góp cụ thể

### P3 — Xác nhận trước khi gửi

Thay chỉ dẫn gửi ngay bằng quy tắc gọi `clarify` với `response_type="yes_no"` trước khi gửi, chỉ gọi `send` sau khi người dùng xác nhận ở lượt sau.

Base eval v3 đạt **16/20 case (80%)**, bằng điểm tổng v2. R12 chuyển từ gọi `send` sang `clarify`, nhưng vẫn dùng `response_type="text"` nên chưa PASS. R10/R11 vẫn thiếu tham số `response_type`; M06 vẫn gọi thừa `social_search`.

Giả thuyết được hỗ trợ một phần ở việc thay đổi lựa chọn tool tại R12, chưa đạt đầy đủ yêu cầu xác nhận. Hash khai báo tool giữa hai run v2 và v3 khác nhau, nên chưa thể quy toàn bộ khác biệt cho prompt. Kiểm thử tại mốc P3 đạt **89 passed**.

### P4 — Làm rõ khai báo tool

Tích hợp khai báo v4, mô tả rõ công dụng, trường hợp dùng/không dùng và quy ước tham số. Giữ nguyên prompt của v3.

Base eval tăng từ **16/20 (80%) lên 19/20 (95%)**. R11, R12 và M06 chuyển FAIL → PASS; không có case PASS → FAIL trong lượt chạy này.

R10 vẫn FAIL nhưng nguyên nhân thay đổi: model gọi `social_search` với `query=""` thay vì hỏi tài khoản. Tool trả các bài đăng không liên quan, cho thấy cần xem cả lời gọi lẫn kết quả thực thi.

Kiểm thử tại mốc P4 đạt **104 passed**. P6a đã được tích hợp giữa hai mốc kiểm thử P3 và P4, nên số test tăng không phải là số test do cá nhân tôi viết. So sánh hai lượt cũng chưa phải phép thử hoàn toàn cô lập mọi thay đổi code.

### P6b — Tích hợp v5 và eval nhóm

Tích hợp snapshot v5 vào prompt và khai báo tool đang dùng, bổ sung khai báo cho `wikipedia`, `hackernews`, `github_repos`, `hf_models` cùng 10 case nhóm gồm 5 single turn và 5 multi turn.

| Bộ eval v5 | PASS | Accuracy |
|---|---:|---:|
| Base | 20/20 | 100% |
| Group | 9/10 | 90% |
| Extension | 9/10 | 90% |

Kiểm thử sau tích hợp đạt **124 passed, không có FAIL hoặc SKIP**. Đây là kết quả toàn bộ bộ test nhóm tại thời điểm chạy.

Base tăng từ 95% ở v4 lên 100% ở v5; R10 đã PASS. Các case kiểm tra routing tới bốn tool mới trong group đều PASS về lựa chọn tool và tham số.

Hai case chưa đạt được phân tích như sau:

- **G10:** người dùng hủy gửi và chuyển sang tìm tin công nghệ. Model không gọi `send`, nhưng gọi `lookup` hai lần thay vì một lần nên bị chấm `extra_tool_call`. Không kết luận agent vẫn gửi sau khi bị hủy.
- **E06:** model chỉ gọi `policy`, thiếu `lookup` theo tiêu chí eval. Vì yêu cầu có thứ tự “kiểm tra policy trước”, cần kiểm chứng thêm trong chat nhiều vòng để đánh giá khả năng hoàn thành toàn bộ yêu cầu.

Riêng **G07** PASS về lời gọi `send`, nội dung và `confirmed=true`, nhưng kết quả thực thi trả `RuntimeError`. Do đó chưa có bằng chứng gửi Telegram thành công.

## 4. Bằng chứng

Các đường dẫn dưới đây tính từ vị trí file báo cáo trong `report/team/`.

| Hạng mục | File bằng chứng |
|---|---|
| Snapshot P3 | [Prompt v3](../../starter_v0/artifacts/versions/v3/system_prompt.md), [tools v3](../../starter_v0/artifacts/versions/v3/tools.yaml) |
| Snapshot P4 | [Prompt v4](../../starter_v0/artifacts/versions/v4/system_prompt.md), [tools v4](../../starter_v0/artifacts/versions/v4/tools.yaml) |
| Snapshot P6b | [Prompt v5](../../starter_v0/artifacts/versions/v5/system_prompt.md), [tools v5](../../starter_v0/artifacts/versions/v5/tools.yaml) |
| Run v3 base | [v3 base JSON](../../starter_v0/runs/v3_B_base_openai_20261110T095619294467.json) |
| Run v4 base | [v4 base JSON](../../starter_v0/runs/v4_B_base_openai_20261110T104217023595.json) |
| Run v5 base | [v5 base JSON](../../starter_v0/runs/v5_B_base_openai_20261110T110115868139.json) |
| Run v5 group | [v5 group JSON](../../starter_v0/runs/v5_B_group_openai_20261110T110424113208.json) |
| Run v5 extension | [v5 extension JSON](../../starter_v0/runs/v5_B_extension_openai_20261110T110514233130.json) |
| Version log | [version_log.csv](../../starter_v0/artifacts/version_log.csv) |
| Nhận xét từng phiên bản | [v3](../../starter_v0/analysis/notes_v3.md), [v4](../../starter_v0/analysis/notes_v4.md), [v5](../../starter_v0/analysis/notes_v5.md) |
| Eval nhóm | [eval_group.json](../../starter_v0/data/eval_group.json) |

### Công cụ hỗ trợ và cách kiểm chứng

- **Codex/ChatGPT:** hỗ trợ giải thích yêu cầu, hướng dẫn lệnh, đọc log và soạn báo cáo. Tôi tự thao tác trong Codespaces, chạy eval/test, chỉnh file và thực hiện Git.
- **GitHub Codespaces:** môi trường chạy Linux sau khi môi trường Windows gặp lỗi kiểm soát ứng dụng chặn thư viện.
- **Git/GitHub:** chia nhánh theo P3, P4, P6b; xem diff, chọn đúng file, commit và gửi PR cho nhóm trưởng.
- **OpenAI và API tool:** chạy kiểm chứng thật; key lưu trong `.env`, không đưa vào commit.
- **pytest:** kiểm tra tính tương thích và hành vi code bằng bộ test của nhóm.

Khi phân tích, tôi đối chiếu `expect`, `actual_tool_calls`, `failures`, `observed_mismatch` và `tool_results`, không dùng riêng điểm tổng để kết luận agent đã hoạt động đúng.

## 5. Tự đánh giá

Tôi hoàn thành việc tích hợp và kiểm chứng trong phạm vi P3, P4, P6b. Các kết quả đều có run JSON, snapshot và nhận xét để truy vết. Tôi ghi nhận cả phần chưa đạt thay vì chỉ báo cáo điểm tăng.

Điều học được rõ nhất là cần phân biệt ba mức: chọn đúng tool, truyền đúng tham số và thực thi thành công. P3 cho thấy model có thể hỏi lại nhưng sai kiểu phản hồi; G07 cho thấy eval PASS vẫn có thể đi kèm lỗi thực thi; G10 cho thấy nhãn lỗi ranh giới không đồng nghĩa với việc agent đã gửi trái ý người dùng.

Các lượt eval dùng cùng model OpenAI gpt-4o-mini nhưng chỉ chạy một lần cho mỗi cấu hình. Kết quả chưa thể hiện đầy đủ độ dao động; các thay đổi code giữa một số mốc cũng giới hạn khả năng kết luận quan hệ nguyên nhân.

Hướng cải thiện tiếp theo là kiểm tra chat nhiều vòng cho yêu cầu có thứ tự, xử lý lời gọi tìm kiếm thừa, chặn truy vấn rỗng và đánh giá cả kết quả thực thi tool. Trước khi demo, tôi cần giải thích được các trường hợp R12, R10, G07, G10 và E06 từ log đã lưu.