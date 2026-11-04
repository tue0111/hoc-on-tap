# ngan-hang-thuong-mai eval _run1

eval sha256 `3d3dbe4bccd66897c6c84ce0c7f8e74951a8b7c687f297486f538372670fcb9b` · n=20 · all_pass=True

| gate | value | threshold | pass |
|---|---|---|---|
| direct_must_include | 0.9166666666666666 | 0.85 | True |
| direct_chapter_at1 | 0.8333333333333334 | 0.8 | True |
| source_bound | 1.0 | 0.6666666666666666 | True |
| insufficient | 1.0 | 1.0 | True |
| collision_contamination | 0 | 0 | True |
| account | None | 0.5 | True |
| topic_owner | None | 1.0 | True |

## failing rows
- nh-d01 (direct): Ngân hàng thương mại: khái niệm và đặc điểm của ngân hàng thương mại là gì? → cov=partial top=['src-0123', 'src-0122', 'src-0132', 'src-0133', 'src-0126'] ch=[2, 1, 1, 2, 5] unknowns=['no_course_concept_match']
- nh-d11 (direct): Ngân hàng thương mại: dịch vụ thanh toán gồm những phương thức nào? → cov=sufficient top=['src-0128', 'src-0123', 'src-0128', 'src-0121', 'src-0123'] ch=[None, 2, None, 0, 2] unknowns=[]