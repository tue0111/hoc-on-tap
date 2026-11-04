# G3g — learner-notes: PASS (isolated non-curriculum partition)

Đã chọn và hash-check 14/14 file `learner_material` từ override và quy tắc path. Extraction tạo 14 document / 132 trang hoặc slide / 276.921 ký tự / 0 lỗi / 0 page-count mismatch. PDF, DOCX và TXT có text; `src-0165` gồm 14 slide chỉ chứa picture, không có title/text frame nên được ghi nhận `thin` với 0 ký tự và không tạo chunk nội dung (không OCR hay suy diễn nội dung ảnh).

Partition `learner-notes` gồm 307 chunk, vocab 2.083, đặt tại `data/indexes/3.0.0/learner-notes/`. Mỗi chunk giữ `course_id` của thư mục gốc, `partition: learner_notes`, `authority: 7`, `content_role: learner_material`. Tất cả document có text đều có chunk; mọi source hash thuộc inventory. Quét toàn bộ các file chunk khác cho kết quả không có learner-material trong bất kỳ partition môn học/core nào.

Eval 5 họ nguồn đã đóng băng ngay sau lần chạy đầu (`sha256 90827db034bb78c377eeebaf47e037da58e5158be176fcd63789b036a989d3f6`).

| gate | giá trị | kết quả |
|---|---:|---|
| đúng họ file trong top-3 | 5/5 | PASS |
| routing bằng learner cue | 5/5 | PASS |
| routing explicit `learner-notes` | 1/1 | PASS |
| coverage = `learner_material` | 5/5 | PASS |
| unknowns = `[not_curriculum_source]` | 5/5 | PASS |
| metadata authority/content_role/partition | 5/5 | PASS |
| learner-material lẫn vào course/core partition | 0 | PASS |

Smoke test xác nhận truy vấn không có learner cue vẫn route về course partition bình thường; câu trả lời learner-notes mở đầu bằng “Tài liệu cá nhân của bạn, không phải giáo trình.” Core regression: `IDENTICAL` (`reports/v3/run_20261011_120737`).
