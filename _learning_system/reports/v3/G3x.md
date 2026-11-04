# G3x — Amendment A1 checkpoint: FAIL

Đã xác minh SHA-256 của 7 eval frozen rồi chạy lại nguyên trạng cho mọi môn đang ở tier `retrieval` (không gồm partition đặc biệt `learner-notes`, đã qua gate G3g riêng). Ba môn đạt toàn bộ gate; bốn môn chỉ đạt `insufficient = 2/3`, dưới yêu cầu 100% của Amendment A1.

| course | direct include@5 | chapter@1 | source-bound | insufficient | collision | account/topic | G3x |
|---|---:|---:|---:|---:|---:|---:|---|
| ke-toan-tai-chinh-2 | 1.000 | 0.900 | 1.000 | **0.667** | 0 | 1.000 / 1.000 | FAIL → catalog |
| kiem-toan-1 | 1.000 | 1.000 | 1.000 | **0.667** | 0 | n/a | FAIL → catalog |
| kinh-doanh-va-nghiep-vu | 1.000 | 1.000 | 1.000 | **0.667** | 0 | n/a | FAIL → catalog |
| luat-kinh-doanh | 1.000 | 0.917 | 1.000 | 1.000 | 0 | n/a | PASS |
| ngan-hang-thuong-mai | 0.917 | 0.833 | 1.000 | 1.000 | 0 | n/a | PASS |
| thi-truong-tai-chinh | 1.000 | 1.000 | 1.000 | 1.000 | 0 | n/a | PASS |
| tai-chinh-hanh-chinh-su-nghiep | 1.000 | 0.833 | 0.667 | **0.667** | 0 | n/a | FAIL → catalog |

## Failing frozen rows

- `k2-i02` và `kt-i03` (giá thành theo quy trình): coverage chỉ `partial`; A1 tạo `no_course_concept_match` và `topic_owner_hint:ke-toan-chi-phi`, nhưng hint không phải điều kiện chuyển sang `insufficient` và KTCP hiện là `catalog` nên không tham gia rival-coverage.
- `kd-i03` (thuế thu nhập hoãn lại): coverage `partial`; có `no_course_concept_match` nhưng không đạt điều kiện OOV hoặc rival-coverage của A1.
- `hcsn-i03` (bao thanh toán NHTM): câu frozen chứa cue của hai môn; router để `course_scope_unresolved` và trả `partial` từ legacy core.

Sửa các trường hợp này đòi thay engine/routing hoặc sửa eval frozen, đều nằm ngoài quyền tuning tại G3x. D1 không được áp dụng và không có eval nào bị sửa.

Theo Amendment A1, bốn môn trượt đã được trả về tier `catalog` và ghi escalation. Các môn vẫn ở retrieval tier sau G3x: `luat-kinh-doanh`, `ngan-hang-thuong-mai`, `thi-truong-tai-chinh`; partition `learner-notes` vẫn retrieval theo gate riêng.

Core regression sau khi cập nhật tier: `IDENTICAL` (`reports/v3/run_20261011_122633`). Wave 4 chưa được bắt đầu.
