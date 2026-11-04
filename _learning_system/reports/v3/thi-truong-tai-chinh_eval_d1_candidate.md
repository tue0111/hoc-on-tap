# thi-truong-tai-chinh eval _d1_candidate

eval sha256 `2fcdb4464517dde4735bab3556afa5df6a223dfbf443d5ae48c9c0cf9fd20dea` · n=20 · all_pass=True

| gate | value | threshold | pass |
|---|---|---|---|
| direct_must_include | 1.0 | 0.85 | True |
| direct_chapter_at1 | 0.9166666666666666 | 0.8 | True |
| source_bound | 0.6666666666666666 | 0.6666666666666666 | True |
| insufficient | 1.0 | 1.0 | True |
| collision_contamination | 0 | 0 | True |
| account | None | 0.5 | True |
| topic_owner | None | 1.0 | True |

## failing rows
- tt-d01 (direct): Thị trường tài chính: thị trường nợ khác thị trường vốn cổ phần như thế nào? → cov=partial top=['src-0151', 'src-0141', 'src-0141', 'src-0144', 'src-0141'] ch=[4, 1, 1, 4, 1] unknowns=['no_course_concept_match']
- tt-s01 (source_bound): Theo Slide Chương 1 môn Thị trường tài chính, các cách phân loại thị trường tài chính gồm gì? → cov=sufficient top=['src-0141', 'src-0141', 'src-0141', 'src-0141', 'src-0141'] ch=[1, 1, 1, 1, 1] unknowns=[]