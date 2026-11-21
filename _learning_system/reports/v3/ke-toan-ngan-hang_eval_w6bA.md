# ke-toan-ngan-hang eval _w6bA

eval sha256 `07d8958ebd6610048cf631970dffa69f039051ab3198eb9f4508c3f073d283b2` · n=22 · all_pass=True

| gate | value | threshold | pass |
|---|---|---|---|
| direct_must_include | 1.0 | 0.85 | True |
| direct_chapter_at1 | 0.8333333333333334 | 0.8 | True |
| source_bound | 1.0 | 0.6666666666666666 | True |
| insufficient | 1.0 | 1.0 | True |
| collision_contamination | 0 | 0 | True |
| account | 1.0 | 0.5 | True |
| topic_owner | None | 1.0 | True |

## failing rows
- kn-d02 (direct): Kế toán ngân hàng: kế toán nghiệp vụ tiền mặt gồm những nội dung nào? → cov=sufficient top=['src-0271', 'src-0265', 'src-0265', 'src-0296', 'src-0265'] ch=[4, 2, 2, 8, 2] unknowns=[]
- kn-d06 (direct): Kế toán ngân hàng: kế toán nghiệp vụ cho vay hạch toán thế nào? → cov=sufficient top=['src-0271', 'src-0278', 'src-0278', 'src-0278', 'src-0278'] ch=[4, 5, 5, 5, 5] unknowns=[]