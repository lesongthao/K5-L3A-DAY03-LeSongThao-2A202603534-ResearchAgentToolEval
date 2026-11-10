# P8 — Small Local Model Challenge

## Thiết lập và giả thuyết

- Model local: `qwen2.5:7b` qua Ollama, chạy trên CPU.
- Suite: `data/eval_base.json` (20 case).
- So sánh: prompt/tools v5 gốc, artifacts `v4-local`, artifacts `v5-local`; chạy thêm `v5-local` trên OpenRouter làm đối chứng cloud.
- Giả thuyết: mô tả tool ngắn gọn, ít tool hơn và ví dụ cụ thể sẽ giúp model nhỏ chọn tool và tạo arguments chính xác hơn.

## Kết quả cloud đối chứng

- Run: `runs/v5-local-on-cloud_B_base_openrouter_20261110T113642425557.json`.
- Kết quả: 19/20 case đạt; case accuracy 0.95; tool routing accuracy 0.95; argument accuracy 0.95; multiturn accuracy 0.8333.
- Provider errors: 0.
- Lỗi: `M06_switch_tool`, phân loại `wrong_tool` (thừa lời gọi tool).

## Trạng thái chạy local

- Đã cài Ollama và tải model `qwen2.5:7b` (4.7 GB).
- Run `v5-qwen7b`: `runs/v5-qwen7b_B_base_ollama_20261110T123327950590.json`; đủ 20 case nhưng cả 20 gặp `provider_error` do `llama-server process has terminated: signal: terminated`. Không có case nào được đo, vì vậy không dùng run này làm metric.
- Chưa chạy được các cấu hình `v4-local-qwen7b` và `v5-local-qwen7b`; cần môi trường Ollama ổn định để hoàn tất và so sánh định lượng.
