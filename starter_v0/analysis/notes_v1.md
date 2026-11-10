# P1 — trạng thái: đã chuẩn bị code, chờ eval thật

- Mốc P0 của Nguyễn Khôi Nguyên: `runs/v0_B_base_openrouter_20261110T104242979050.json`, OpenRouter / `openai/gpt-4o-mini`, case_accuracy **0.70**. Giữ nguyên run và dòng v0 trong `artifacts/version_log.csv`.
- Lấy đúng snapshot v1 từ `team-kit`: chỉ thay chỉ dẫn "single step, pick one tool" bằng quy tắc trả lời không dùng tool khi phù hợp và gọi nhiều tool khi cần nhiều nguồn. `tools.yaml` giữ nguyên như v0; chưa áp dụng v2–v5.
- Giả thuyết cần kiểm chứng: R08/R14 giảm gọi tool thừa, R13 gọi đủ các nguồn; các case khác không bị giảm kết quả.
- Chưa chạy eval v1 vì cấu hình hiện tại không có `OPENROUTER_API_KEY`. Chưa biết điểm v1, case chuyển PASS/FAIL hay giả thuyết đúng/sai; không tạo run JSON hoặc dòng version log giả.
- Bàn giao: người có key chạy đúng lệnh P1 trong `PHAN_CONG.md` trên nhánh này, ghi log bằng `scripts/log_version.py`, cập nhật nhận xét từ run thật rồi chuyển PR khỏi draft để merge. Chưa bàn giao P2 như một P1 đã hoàn tất; P6a có thể bắt đầu từ `main` sau P5.
