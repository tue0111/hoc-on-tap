# tai-chinh-doanh-nghiep-1 eval _r1_b

eval sha256 `215d84accd2b20fd242fda49fa5021666b37b7d025edf5185977b109c1073e6d` · n=20 · all_pass=False

| gate | value | threshold | pass |
|---|---|---|---|
| direct_must_include | 0.9166666666666666 | 0.85 | True |
| direct_chapter_at1 | 0.5833333333333334 | 0.8 | False |
| source_bound | 0.6666666666666666 | 0.6666666666666666 | True |
| insufficient | 1.0 | 1.0 | True |
| collision_contamination | 0 | 0 | True |
| account | None | 0.5 | True |
| topic_owner | None | 1.0 | True |

## failing rows
- td-d01 (direct): Tài chính doanh nghiệp 1: môi trường kinh doanh của doanh nghiệp gồm những yếu tố nào? → cov=sufficient top=['src-0177', 'src-0156', 'src-0156', 'src-0168', 'src-0157'] ch=[None, 1, 1, 2, 2] unknowns=[]
- td-d03 (direct): Tài chính doanh nghiệp 1: thời giá tiền tệ của một dòng tiền được tính thế nào? → cov=sufficient top=['src-0155', 'src-0177', 'src-0166', 'src-0158', 'src-0157'] ch=[0, 3, None, 3, 2] unknowns=[]
- td-d04 (direct): Tài chính doanh nghiệp 1: mô hình định giá tài sản vốn CAPM giải thích quan hệ lợi nhuận và rủi ro ra sao? → cov=sufficient top=['src-0177', 'src-0169', 'src-0169', 'src-0159', 'src-0155'] ch=[3, 4, 4, 4, 0] unknowns=[]
- td-d06 (direct): Tài chính doanh nghiệp 1: định giá cổ phiếu thường theo dòng tiền cổ tức ra sao? → cov=partial top=['src-0170', 'src-0177', 'src-0155', 'src-0166', 'src-0156'] ch=[5, 5, 0, None, 1] unknowns=['no_course_concept_match']
- td-d11 (direct): Tài chính doanh nghiệp 1: đòn bẩy kinh doanh và đòn bẩy tài chính khác nhau thế nào? → cov=sufficient top=['src-0155', 'src-0177', 'src-0166', 'src-0163', 'src-0163'] ch=[5, 8, None, 8, 8] unknowns=[]
- td-d12 (direct): Tài chính doanh nghiệp 1: các hình thức chi trả cổ tức và chính sách cổ tức gồm gì? → cov=sufficient top=['src-0177', 'src-0166', 'src-0164', 'src-0156', 'src-0164'] ch=[8, None, 9, 1, 9] unknowns=[]
- td-s02 (source_bound): Đề thi mẫu Tài chính doanh nghiệp 1 có những dạng câu hỏi nào? → cov=sufficient top=['src-0161', 'src-0156', 'src-0175', 'src-0155', 'src-0166'] ch=[6, 1, None, None, None] unknowns=[]