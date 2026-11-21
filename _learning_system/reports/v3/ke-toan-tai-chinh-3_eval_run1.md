# ke-toan-tai-chinh-3 eval _run1

eval sha256 `fbcbcacfa23ce207dbea697065e4ba6be901d92c10a1a27a2cb2ca26ea797868` · n=23 · all_pass=True

| gate | value | threshold | pass |
|---|---|---|---|
| direct_must_include | 0.9166666666666666 | 0.85 | True |
| direct_chapter_at1 | 1.0 | 0.8 | True |
| source_bound | 1.0 | 0.6666666666666666 | True |
| insufficient | 1.0 | 1.0 | True |
| collision_contamination | 0 | 0 | True |
| account | 1.0 | 0.5 | True |
| topic_owner | None | 1.0 | True |

## failing rows
- k3-d04 (direct): Kế toán tài chính 3: bất động sản đầu tư khác bất động sản chủ sở hữu sử dụng như thế nào? → cov=sufficient top=['src-0564', 'src-0555', 'src-0564', 'src-0555', 'src-0594'] ch=[2, 2, 2, 2, None] unknowns=[]