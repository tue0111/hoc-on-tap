# Corpus delta — Phase 2.1

Compared `D:\Hoc` (excluding `_learning_system`) to `inventory/files.json` using **relative_path + size + SHA-256**. Timestamps were not used.

| class | count |
|---|---|
| OLD inventory | 192 |
| NOW on disk | 333 |
| **NEW** | **141** |
| **CHANGED** | **0** |
| **MISSING** | **0** |
| **UNCHANGED** | **192** |

Source IDs `src-0001`–`src-0192` are unchanged. New IDs: `src-0193`–`src-0333`.

## By course

| folder | new | changed | missing | unchanged | retrieval impact |
|---|---|---|---|---|---|
| Nguyên lý kế toán | 0 | 0 | 0 | 28 | **NO_RETRIEVAL_IMPACT** |
| Kế toán tài chính 1 | 0 | 0 | 0 | 12 | **NO_RETRIEVAL_IMPACT** |
| Kế toán tài chính 2 | 31 | 0 | 0 | 7 | METADATA_ONLY (future ingest) |
| Kế toán chi phí | 34 | 0 | 0 | 5 | METADATA_ONLY |
| Kiểm toán 1 | 28 | 0 | 0 | 5 | METADATA_ONLY |
| Kế toán ngân hàng | 48 | 0 | 0 | 10 | METADATA_ONLY |
| All other courses | 0 | 0 | 0 | 130 | NO_RETRIEVAL_IMPACT |

## NEW canonical files (chapter / ôn tập / exam)

**Kiểm toán 1:** Chương 4–6, Hướng dẫn ôn tập, Đề thi mẫu  
**Kế toán chi phí:** Chương 5–7, Hướng dẫn ôn tập, Đề thi mẫu  
**Kế toán ngân hàng:** Chương 6–9, Hướng dẫn ôn tập, Đề thi mẫu  
**Kế toán tài chính 2:** Chương 3–4, Hướng dẫn ôn tập, Đề thi mẫu  

Plus `_nguon/` unit scripts (catalogued, not fully extracted): underlying clip/topic PDFs for those courses.

## NLKT / KTTC1

No new, changed, or missing files. Phase 2 index `data/indexes/2.0.0` was **not** rebuilt.
