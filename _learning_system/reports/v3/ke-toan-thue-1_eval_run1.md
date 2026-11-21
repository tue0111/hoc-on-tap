# ke-toan-thue-1 eval _run1

eval sha256 `3d9eb60aae42b12939cf3a22fb90a9c03e2ba504c196cc29161bad5a7c8a3024` · n=20 · all_pass=True

| gate | value | threshold | pass |
|---|---|---|---|
| direct_must_include | 1.0 | 0.85 | True |
| direct_chapter_at1 | 0.8 | 0.8 | True |
| source_bound | 1.0 | 0.6666666666666666 | True |
| insufficient | 1.0 | 1.0 | True |
| collision_contamination | 0 | 0 | True |
| account | 1.0 | 0.5 | True |
| topic_owner | None | 1.0 | True |

## failing rows
- th-d03 (direct): Kế toán thuế 1: dùng phần mềm HTKK để lập tờ khai thuế như thế nào? → cov=sufficient top=['src-0516', 'src-0536', 'src-0541', 'src-0526', 'src-0496'] ch=[3, 5, None, 4, 1] unknowns=[]
- th-d09 (direct): Kế toán thuế 1: tính thuế GTGT theo phương pháp khấu trừ và phương pháp trực tiếp khác nhau thế nào? → cov=sufficient top=['src-0496', 'src-0532', 'src-0532', 'src-0536', 'src-0541'] ch=[1, 5, 5, 5, None] unknowns=[]