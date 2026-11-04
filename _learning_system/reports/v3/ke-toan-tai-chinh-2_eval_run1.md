# ke-toan-tai-chinh-2 eval _run1

eval sha256 `0c9e52c16751b0829376570b2828e74389b02a820b79b2ce2728c87fb62e1750` · n=23 · all_pass=False

| gate | value | threshold | pass |
|---|---|---|---|
| direct_must_include | 1.0 | 0.85 | True |
| direct_chapter_at1 | 0.9 | 0.8 | True |
| source_bound | 1.0 | 0.6666666666666666 | True |
| insufficient | 0.0 | 1.0 | False |
| collision_contamination | 0 | 0 | True |
| account | 1.0 | 0.5 | True |
| topic_owner | 1.0 | 1.0 | True |

## failing rows
- k2-d01 (direct): Kế toán tài chính 2: tài sản cố định hữu hình được ghi nhận khi nào? → cov=sufficient top=['src-0333', 'src-0306', 'src-0305', 'src-0312', 'src-0306'] ch=[None, 1, None, 1, 1] unknowns=[]
- k2-i01 (insufficient): Mô hình CAPM trong KTTC2 được tính như thế nào? → cov=sufficient top=['src-0325', 'src-0313', 'src-0325', 'src-0307', 'src-0307'] ch=[4, 2, 4, 1, 1] unknowns=[]
- k2-i02 (insufficient): Phương pháp tính giá thành theo quy trình sản xuất trong Kế toán tài chính 2 là gì? → cov=sufficient top=['src-0308', 'src-0308', 'src-0331', 'src-0308', 'src-0075'] ch=[1, 1, 4, 1, None] unknowns=[]
- k2-i03 (insufficient): Kế toán tài chính 2 hướng dẫn xếp hạng tín dụng khách hàng vay ngân hàng thế nào? → cov=sufficient top=['src-0313', 'src-0326', 'src-0315', 'src-0331', 'src-0307'] ch=[2, 4, 2, 4, 1] unknowns=[]