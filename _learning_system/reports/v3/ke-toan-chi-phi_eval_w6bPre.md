# ke-toan-chi-phi eval _w6bPre

eval sha256 `c93ad30bdef0cb1cded0b84dc817b40d7b42e8c12f816d40974bc61659472cca` · n=23 · all_pass=False

| gate | value | threshold | pass |
|---|---|---|---|
| direct_must_include | 0.9 | 0.85 | True |
| direct_chapter_at1 | 0.8 | 0.8 | True |
| source_bound | 1.0 | 0.6666666666666666 | True |
| insufficient | 1.0 | 1.0 | True |
| collision_contamination | 0 | 0 | True |
| account | 1.0 | 0.5 | True |
| topic_owner | 0.0 | 1.0 | False |

## failing rows
- kp-d02 (direct): Trong Kế toán chi phí, biến phí và định phí là gì? → cov=sufficient top=['src-0234', 'src-0233', 'src-0245', 'src-0229', 'src-0233'] ch=[5, 5, 2, 3, 5] unknowns=[]
- kp-d10 (direct): Kế toán chi phí: giá thành khả biến ảnh hưởng thế nào đến báo cáo thu nhập? → cov=sufficient top=['src-0224', 'src-0252', 'src-0252', 'src-0253', 'src-0252'] ch=[None, 7, 7, 7, 7] unknowns=[]
- kp-t01 (topic_owner): Sản lượng tương đương tính thế nào trong KTTC1? → cov=sufficient top=['src-0061', 'src-0061', 'src-0062', 'src-0061', 'src-0061'] ch=[2, 2, 3, 2, 2] unknowns=[]
- kp-t02 (topic_owner): Phương pháp ABC trong KTTC1 là gì? → cov=sufficient top=['src-0062', 'src-0062', 'src-0062', 'src-0062', 'src-0067'] ch=[3, 3, 3, 3, 3] unknowns=[]
- kp-t03 (topic_owner): Giá thành khả biến trong KTTC1 là gì? → cov=sufficient top=['src-0059', 'src-0062', 'src-0060', 'src-0062', 'src-0062'] ch=[0, 3, 1, 3, 3] unknowns=[]