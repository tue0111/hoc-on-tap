# -*- coding: utf-8 -*-
"""W6b step C4: export _grok_pack/<NN>_<course>.md for the 4 new courses, same format as files 01-12.

Source = indexed chunks (data/chunks/<C>.chunks.jsonl): one block per chunk with the label
[course | ch.N | file | tr.a-b | content_role]. Files over SPLIT_BYTES are split into _p1, _p2, ...
Excluded: src-0341 (English commercial reference textbook, 81% of HTTTKT1 text, never in a top-5 of the
course eval) - listed in the TOC as excluded so the tutor knows it exists.
Writes only _grok_pack/<NN>_*.md for these courses; 00_MUC_LUC / 00_HUONG_DAN are edited by hand.
"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from retrieval.config import SYSTEM
from retrieval import courses as C

PACK = SYSTEM.parent / "_grok_pack"
COURSES = [("18", "he-thong-thong-tin-ke-toan-1"), ("19", "ke-toan-thue-1"),
           ("20", "ke-toan-tai-chinh-3"), ("21", "ke-toan-hanh-chinh-su-nghiep")]
EXCLUDE = {"src-0341": "sách tham khảo tiếng Anh (Owen G., Using Microsoft Excel for Accounting), không đưa vào gói"}
SPLIT_BYTES = 560_000


def chap_key(ch):
    return (1, 0) if ch is None else (0, int(ch))


def main():
    toc = {}
    for num, cid in COURSES:
        reg = C.get_course(cid)
        chunks = [json.loads(l) for l in open(SYSTEM / f"data/chunks/{cid}.chunks.jsonl", encoding="utf-8")]
        order = {}
        for i, ch in enumerate(chunks):
            order.setdefault(ch["source_id"], i)
        chunks = [c for c in chunks if c["source_id"] not in EXCLUDE]
        chunks.sort(key=lambda c: (chap_key(c["chapter"]), c["source_file"], c["source_id"], order[c["source_id"]],
                                   c["page_start"] or 0, c["chunk_id"]))
        code = f" ({', '.join(reg['codes'])})" if reg.get("codes") else ""
        head = f"# {reg['name']}\nLoại: GIÁO TRÌNH\nMã môn: {cid}\n\n"
        parts, cur, cur_src, size = [], [], None, 0
        files = []
        for c in chunks:
            block = []
            if c["source_id"] != cur_src:
                chv = "—" if c["chapter"] is None else c["chapter"]
                block.append(f"\n## Chương {chv} · {c['source_file']}\n")
                cur_src = c["source_id"]
                files.append((chv, c["source_file"]))
            ch = "—" if c["chapter"] is None else c["chapter"]
            block.append(f"\n[{cid} | ch.{ch} | {c['source_file']} | tr.{c['page_range']} | {c['content_role']}]\n{c['text'].strip()}\n")
            text = "".join(block)
            if size + len(text.encode("utf-8")) > SPLIT_BYTES and cur:
                parts.append(cur); cur, size = [], 0
            cur.append(text); size += len(text.encode("utf-8"))
        parts.append(cur)
        names = []
        for i, p in enumerate(parts, 1):
            name = f"{num}_{cid}.md" if len(parts) == 1 else f"{num}_{cid}_p{i}.md"
            (PACK / name).write_text(head + "".join(p), encoding="utf-8")
            names.append(name)
        seen, lst = set(), []
        for f in files:
            if f not in seen:
                seen.add(f); lst.append(f)
        toc[cid] = {"name": reg["name"] + code, "files": names, "sources": lst, "chunks": len(chunks),
                    "excluded": [v for k, v in EXCLUDE.items() if any(r["source_id"] == k for r in
                                 map(json.loads, open(SYSTEM / f"data/chunks/{cid}.chunks.jsonl", encoding="utf-8")))]}
        print(cid, names, len(chunks), "chunks")
    (SYSTEM / "work/w6b/grok_pack_toc.json").write_text(json.dumps(toc, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
