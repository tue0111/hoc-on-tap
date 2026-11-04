# kiem-toan-1 eval _g3x

eval sha256 `8e1df7c48a6fe2b99f0b6eaa78c1f2e8c16da74d1647a1d45f8ab8700547c34b` · n=20 · all_pass=False

| gate | value | threshold | pass |
|---|---|---|---|
| direct_must_include | 1.0 | 0.85 | True |
| direct_chapter_at1 | 1.0 | 0.8 | True |
| source_bound | 1.0 | 0.6666666666666666 | True |
| insufficient | 0.6666666666666666 | 1.0 | False |
| collision_contamination | 0 | 0 | True |
| account | None | 0.5 | True |
| topic_owner | None | 1.0 | True |

## failing rows
- kt-i03 (insufficient): Kiểm toán 1: phương pháp tính giá thành theo quy trình sản xuất là gì? → cov=partial top=['src-0215', 'src-0197', 'src-0215', 'src-0207', 'src-0200'] ch=[5, 1, 5, 4, 2] unknowns=['no_course_concept_match', 'topic_owner_hint:ke-toan-chi-phi']