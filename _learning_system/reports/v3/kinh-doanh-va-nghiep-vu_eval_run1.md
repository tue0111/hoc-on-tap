# kinh-doanh-va-nghiep-vu eval _run1

eval sha256 `892eeb3f66ca29e2f4d96613767f2854386c42a039b9b8f4a436c6b3fb381e38` · n=20 · all_pass=False

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
- kd-i03 (insufficient): Kinh doanh và nghiệp vụ hướng dẫn hạch toán thuế thu nhập hoãn lại ra sao? → cov=partial top=['src-0008', 'src-0016', 'src-0006', 'src-0034', 'src-0020'] ch=[1, 3, 1, None, 3] unknowns=['no_course_concept_match']