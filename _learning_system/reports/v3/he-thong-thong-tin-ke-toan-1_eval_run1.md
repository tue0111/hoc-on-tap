# he-thong-thong-tin-ke-toan-1 eval _run1

eval sha256 `dee08790290945add182df20591b77d24c1bb00df58a84661e4f6e81bb890792` · n=24 · all_pass=True

| gate | value | threshold | pass |
|---|---|---|---|
| direct_must_include | 1.0 | 0.85 | True |
| direct_chapter_at1 | 0.9285714285714286 | 0.8 | True |
| source_bound | 0.6666666666666666 | 0.6666666666666666 | True |
| insufficient | 1.0 | 1.0 | True |
| collision_contamination | 0 | 0 | True |
| account | 1.0 | 0.5 | True |
| topic_owner | None | 1.0 | True |

## failing rows
- ht-d09 (direct): Hệ thống thông tin kế toán 1: lập sổ cái tài khoản tổng hợp trên bảng tính thế nào? → cov=sufficient top=['src-0390', 'src-0343', 'src-0389', 'src-0406', 'src-0378'] ch=[5, 1, 5, None, 4] unknowns=[]
- ht-s02 (source_bound): Đề thi mẫu HTTTKT1 gồm những câu hỏi nào? → cov=sufficient top=['src-0406', 'src-0344', 'src-0365', 'src-0364', 'src-0363'] ch=[None, 1, 3, 3, 3] unknowns=[]