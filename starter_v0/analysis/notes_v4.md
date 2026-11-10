Run: runs/v4_B_base_openai_20261110T104217023595.json, OpenAI gpt-4o-mini.
Điểm tăng từ 16/20 lên 19/20, tương đương 80% → 95%.
R11, R12, M06 chuyển FAIL → PASS; không có case PASS → FAIL.
R10 vẫn FAIL: gọi social_search với query rỗng thay vì hỏi tài khoản.
Prompt hash giữ nguyên; thay khai báo tool hỗ trợ cải thiện trong lượt chạy này. Code tool cũng thay đổi giữa hai mốc do P6a đã được merge, nên chưa coi đây là phép thử hoàn toàn cô lập.