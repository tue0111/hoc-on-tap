# ke-toan-hanh-chinh-su-nghiep eval _run1

eval sha256 `03e575bc1ac60ea770a362c0c7b5b50308b355972dac5184feac2b5e1c7d201d` · n=21 · all_pass=True

| gate | value | threshold | pass |
|---|---|---|---|
| direct_must_include | 1.0 | 0.85 | True |
| direct_chapter_at1 | 0.9 | 0.8 | True |
| source_bound | 1.0 | 0.6666666666666666 | True |
| insufficient | 1.0 | 1.0 | True |
| collision_contamination | 0 | 0 | True |
| account | 1.0 | 0.5 | True |
| topic_owner | None | 1.0 | True |

## failing rows
- kthcsn-d01 (direct): Kế toán hành chính sự nghiệp: tổ chức công tác kế toán tại đơn vị gồm những nội dung nào? → cov=sufficient top=['src-0489', 'src-0407', 'src-0489', 'src-0409', 'src-0407'] ch=[None, 1, None, 1, 1] unknowns=[]