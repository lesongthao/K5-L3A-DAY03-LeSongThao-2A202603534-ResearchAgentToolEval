Provider/model là OpenAI gpt-4o-mini.
Base 20/20, group 9/10, extension 9/10; unit test 124 passed.
Base tăng từ 95% ở v4 lên 100% ở v5 trong lượt chạy này.
Điểm eval đo chọn tool/tham số, không đảm bảo mọi tool thực thi thành công.

Base run: runs/v5_B_base_openai_20261110T110115868139.json
Group run: runs/v5_B_group_openai_20261110T110424113208.json
Extension run: runs/v5_B_extension_openai_20261110T110514233130.json
G10: không gọi send sau khi user hủy; FAIL vì gọi lookup hai lần thay vì một lần.
E06: chỉ gọi policy, thiếu lookup theo yêu cầu của eval; cần kiểm tra thêm trong chat nhiều vòng vì user yêu cầu kiểm tra policy trước.
G07: PASS về tool và tham số xác nhận, nhưng tool trả RuntimeError; chưa có bằng chứng gửi Telegram thành công.