# tai-chinh-hanh-chinh-su-nghiep eval _wave5

eval sha256 `6365ddfa557dd2caeee16bb2ffa75173e1fc78ce208d74a9998dde4452689b24` · n=20 · all_pass=True

| gate | value | threshold | pass |
|---|---|---|---|
| direct_must_include | 1.0 | 0.85 | True |
| direct_chapter_at1 | 0.8333333333333334 | 0.8 | True |
| source_bound | 0.6666666666666666 | 0.6666666666666666 | True |
| insufficient | 1.0 | 1.0 | True |
| collision_contamination | 0 | 0 | True |
| account | None | 0.5 | True |
| topic_owner | None | 1.0 | True |

## failing rows
- hcsn-d04 (direct): Tài chính hành chính sự nghiệp: đơn vị sự nghiệp công lập thực hiện tự chủ tài chính ra sao? → cov=partial top=['src-0179', 'src-0180', 'src-0180', 'src-0180', 'src-0187'] ch=[1, 2, 2, 2, 1] unknowns=['no_course_concept_match']
- hcsn-d08 (direct): Tài chính hành chính sự nghiệp: chi phí quản lý dự án đầu tư xây dựng được quản lý thế nào? → cov=partial top=['src-0185', 'src-0182', 'src-0190', 'src-0190', 'src-0182'] ch=[None, 4, 4, 4, 4] unknowns=['no_course_concept_match']
- hcsn-s01 (source_bound): Theo đề thi mẫu TCHCSN năm 2022, cấu trúc đề và thời lượng thi là gì? → cov=sufficient top=['src-0184', 'src-0184', 'src-0184', 'src-0182', 'src-0192'] ch=[6, 6, 6, 4, None] unknowns=[]