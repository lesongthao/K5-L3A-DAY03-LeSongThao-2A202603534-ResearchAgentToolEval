# Báo cáo cá nhân — Dương Quang Bảo

## 1. Thông tin thành viên

- Họ tên: Dương Quang Bảo
- MSSV: 2A202603362
- Email: 26ai.baodq3@vinuni.edu.vn

## 2. Phần việc phụ trách

- Thực hiện bonus P8 — Small Local Model Challenge với Qwen 2.5 7B.
- Đánh giá cấu hình prompt/tools local v5 bằng OpenRouter để có số liệu đối chiếu.

## 3. Đóng góp cụ thể

- Nhánh `DuongQuangBao_2A202603362` — commit `d946474`:
  - Triển khai UI Streamlit ban đầu tại `starter_v0/app.py`, cập nhật hướng dẫn và dependency chạy UI.
  - Chạy eval baseline `v0` trên OpenRouter: 14/20 case đạt (case accuracy 0.70), không có provider error.
  - Lưu transcript chat live gồm 3 lượt.
- P7a — nhánh `quangbao-p7a`:
  - Cập nhật UI Streamlit, tạo poster giới thiệu agent và script/transcript demo chat live.
- Tạo nhánh `quangbao-p8` từ `origin/main` và lấy các artifacts local v4/v5 từ `origin/team-kit`.
- Cài Ollama trên môi trường Linux và khởi động Ollama API ở `127.0.0.1:11434`.
- Chạy eval suite `base` trên OpenRouter với prompt/tools `artifacts/local/v5-local`.
  - Kết quả: 19/20 case đạt; `case_accuracy`, `tool_routing_accuracy` và `argument_accuracy` đều là 0.95; `multiturn_accuracy` là 0.8333.
  - Không có provider error; lỗi duy nhất là `wrong_tool` ở case `M06_switch_tool`.
- Ghi run `v5-local-on-cloud` vào `artifacts/version_log.csv`.
- Tải model `qwen2.5:7b` (4.7 GB) thành công và chạy eval `v5-qwen7b` đủ 20 case; Ollama gặp lỗi khởi chạy `llama-server` ở cả 20 case (`provider_error_cases=20`), nên không có metric local hợp lệ. Hai cấu hình local v4/v5 chưa chạy được do cùng lỗi provider.

## 4. Bằng chứng

- Nhánh làm việc: `quangbao-p8`.
- Bằng chứng nhánh `DuongQuangBao_2A202603362`: commit `d946474` (`feat: implement v0`), run `starter_v0/runs/v0_B_base_openrouter_20261110T032941707184.json`, transcript `starter_v0/transcripts/v0_openrouter_20261110T033831997671.transcript.json`.
- Bằng chứng P7a: nhánh `quangbao-p7a`, commit `f430efb` (`ui: Streamlit app, poster, and live chat transcripts`); các file gồm `starter_v0/app.py`, `starter_v0/artifacts/poster.html`, `starter_v0/scripts/run_chat_demo.py`, và `starter_v0/transcripts/ui_v5_openrouter_20261110T091152890665.transcript.json`.
- Ollama provider trong `starter_v0/providers/ollama_provider.py` được thêm bởi commit `533b78c` của thành viên khác; P8 sử dụng provider có sẵn này, không tính là phần đóng góp P7a của tôi.
- Artifacts lấy từ team-kit: `starter_v0/artifacts/local/v4-local/` và `starter_v0/artifacts/local/v5-local/`.
- Run local lỗi provider (được lưu làm bằng chứng, không dùng để tính điểm): `starter_v0/runs/v5-qwen7b_B_base_ollama_20261110T123327950590.json`.
- Run cloud: `starter_v0/runs/v5-local-on-cloud_B_base_openrouter_20261110T113642425557.json`.
- Version log: `starter_v0/artifacts/version_log.csv`, dòng `v5-local-on-cloud`.
- Eval command:
  `python run_eval.py --provider openrouter --version v5-local-on-cloud --suite base --eval-cases data/eval_base.json --system-prompt artifacts/local/v5-local/system_prompt.md --tools artifacts/local/v5-local/tools.yaml`
- AI/công cụ đã dùng: Copilot SDK trong VS Code, Git, Python, OpenRouter và Ollama. Tự kiểm tra bằng số liệu từ run JSON, `provider_error_cases` và phản hồi của Ollama API.

## 5. Tự đánh giá

- Đã hoàn thành thiết lập nhánh, artifacts local và lượt đánh giá cloud đầu tiên.
- Chưa có kết quả để kết luận Qwen 2.5 7B chạy local tốt hơn hay kém hơn cloud. Cần chạy lại trên môi trường Ollama hoạt động ổn định và hoàn tất các cấu hình v5, v4-local, v5-local.
- Run cloud cho thấy cấu hình local v5 đạt 95% case accuracy trên bộ base; M06 là case cần xem lại khi phân tích kết quả local.
