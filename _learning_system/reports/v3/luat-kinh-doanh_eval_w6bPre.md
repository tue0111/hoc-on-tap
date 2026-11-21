# luat-kinh-doanh eval _w6bPre

eval sha256 `1d66c7351b6d868e3f9282645f85fc3ec2b32e75b77d62db6af391a8e8263045` · n=20 · all_pass=True

| gate | value | threshold | pass |
|---|---|---|---|
| direct_must_include | 1.0 | 0.85 | True |
| direct_chapter_at1 | 0.9166666666666666 | 0.8 | True |
| source_bound | 1.0 | 0.6666666666666666 | True |
| insufficient | 1.0 | 1.0 | True |
| collision_contamination | 0 | 0 | True |
| account | None | 0.5 | True |
| topic_owner | None | 1.0 | True |

## failing rows
- lk-d05 (direct): Luật kinh doanh: công ty hợp danh khác doanh nghiệp tư nhân như thế nào? → cov=sufficient top=['src-0078', 'src-0083', 'src-0083', 'src-0079', 'src-0080'] ch=[None, 2, 2, 1, 2] unknowns=[]