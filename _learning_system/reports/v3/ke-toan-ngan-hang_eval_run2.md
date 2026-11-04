# ke-toan-ngan-hang eval _run2

eval sha256 `07d8958ebd6610048cf631970dffa69f039051ab3198eb9f4508c3f073d283b2` · n=22 · all_pass=False

| gate | value | threshold | pass |
|---|---|---|---|
| direct_must_include | 0.9166666666666666 | 0.85 | True |
| direct_chapter_at1 | 0.75 | 0.8 | False |
| source_bound | 1.0 | 0.6666666666666666 | True |
| insufficient | 1.0 | 1.0 | True |
| collision_contamination | 0 | 0 | True |
| account | 1.0 | 0.5 | True |
| topic_owner | None | 1.0 | True |

## failing rows
- kn-d02 (direct): Kế toán ngân hàng: kế toán nghiệp vụ tiền mặt gồm những nội dung nào? → cov=sufficient top=['src-0271', 'src-0265', 'src-0265', 'src-0265', 'src-0296'] ch=[4, 2, 2, 2, 8] unknowns=[]
- kn-d06 (direct): Kế toán ngân hàng: kế toán nghiệp vụ cho vay hạch toán thế nào? → cov=sufficient top=['src-0271', 'src-0278', 'src-0278', 'src-0278', 'src-0278'] ch=[4, 5, 5, 5, 5] unknowns=[]
- kn-d10 (direct): Kế toán ngân hàng: bảng cân đối kế toán của ngân hàng thương mại trình bày thế nào? → cov=partial top=['src-0103', 'src-0097', 'src-0058', 'src-0062', 'src-0062'] ch=[2, 2, None, 3, 3] unknowns=['course_scope_unresolved']