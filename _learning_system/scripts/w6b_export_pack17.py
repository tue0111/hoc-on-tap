# -*- coding: utf-8 -*-
"""Export _grok_pack/17_van-ban-phap-quy.md + its TOC block from data/chunks/external.chunks.jsonl (keeps evidence labels)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from retrieval.config import SYSTEM
PACK = SYSTEM.parent / "_grok_pack"
ch = sorted((json.loads(l) for l in open(SYSTEM / "data/chunks/external.chunks.jsonl", encoding="utf-8")),
            key=lambda c: (c["source_file"], c["chunk_id"]))
out = ["# Quy định hiện hành (nguồn ngoài giáo trình)\nLoại: VĂN BẢN PHÁP QUY (nguồn ngoài giáo trình, đối chiếu hiệu lực)\nMã môn: external\n\n"]
cur = None
for c in ch:
    if c["source_file"] != cur:
        out.append(f"\n## Chương — · {c['source_file']}\n"); cur = c["source_file"]
    pg = f" | tr.{c['page_range']}" if c.get("page_range") else ""
    out.append(f"\n[external | ch.— | {c['source_file']}{pg} | external | {c.get('url') or '—'} | {c.get('evidence_status')}]\n{c['text'].strip()}\n")
files = sorted({c["source_file"] for c in ch})
p = PACK / "00_MUC_LUC.md"; s = p.read_text(encoding="utf-8")
i = s.index("## 17_van-ban-phap-quy.md")  # fail BEFORE writing anything if the TOC has no section 17 (W6b review G14)
j = s.find("\n## ", i + 5)
j = len(s) if j < 0 else j  # section 17 may be the last one in the TOC
(PACK / "17_van-ban-phap-quy.md").write_text("".join(out), encoding="utf-8")
blk = ("## 17_van-ban-phap-quy.md\nQuy định hiện hành (nguồn ngoài giáo trình) · Loại: VĂN BẢN PHÁP QUY (nguồn ngoài giáo trình, đối chiếu hiệu lực)\n"
       + "".join(f"- Chương — · {f}\n" for f in files))
p.write_text(s[:i] + blk.rstrip("\n") + "\n" + s[j:], encoding="utf-8")
print(len(ch), "chunks", len(files), "files")
