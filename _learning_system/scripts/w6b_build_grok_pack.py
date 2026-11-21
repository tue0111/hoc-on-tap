# -*- coding: utf-8 -*-
"""W6b step C4: export _grok_pack/<NN>_<course>.md for the 4 new courses, same format as files 01-12.

Source = indexed chunks (data/chunks/<C>.chunks.jsonl): one block per chunk with the label
[course | ch.N | file | tr.a-b | content_role]. Files over SPLIT_BYTES are split into _p1, _p2, ...
Excluded: src-0341 (English commercial reference textbook, 81% of HTTTKT1 text, never in a top-5 of the
course eval) - listed in the TOC as excluded so the tutor knows it exists.
Idempotent: also rewrites the TOC blocks 18+ in 00_MUC_LUC.md from scratch, listing per part the files that
really land in that part (W6b review G15). 00_HUONG_DAN_GROK.md and README are edited by hand.
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
NL = "\n"


def chap_key(ch):
    return (1, 0) if ch is None else (0, int(ch))


def heading(c):
    chv = "—" if c["chapter"] is None else c["chapter"]
    return f"{NL}## Chương {chv} · {c['source_file']}{NL}"


def main():
    toc = {}
    for num, cid in COURSES:
        reg = C.get_course(cid)
        all_chunks = [json.loads(l) for l in open(SYSTEM / f"data/chunks/{cid}.chunks.jsonl", encoding="utf-8")]
        order = {}
        for i, ch in enumerate(all_chunks):
            order.setdefault(ch["source_id"], i)
        excluded = [v for k, v in EXCLUDE.items() if any(r["source_id"] == k for r in all_chunks)]
        chunks = [c for c in all_chunks if c["source_id"] not in EXCLUDE]
        chunks.sort(key=lambda c: (chap_key(c["chapter"]), c["source_file"], c["source_id"], order[c["source_id"]],
                                   c["page_start"] or 0, c["chunk_id"]))
        code = f" ({', '.join(reg['codes'])})" if reg.get("codes") else ""
        head = f"# {reg['name']}{NL}Loại: GIÁO TRÌNH{NL}Mã môn: {cid}{NL}{NL}"
        parts, cur, cur_src, size = [], [], None, 0
        part_files = [[]]
        for c in chunks:
            ch = "—" if c["chapter"] is None else c["chapter"]
            label = f"{NL}[{cid} | ch.{ch} | {c['source_file']} | tr.{c['page_range']} | {c['content_role']}]{NL}{c['text'].strip()}{NL}"
            new_source = c["source_id"] != cur_src
            text = (heading(c) if new_source else "") + label
            if size + len(text.encode("utf-8")) > SPLIT_BYTES and cur:
                parts.append(cur); cur, size = [], 0
                part_files.append([])
                if not new_source:  # a part always opens with its source heading
                    text = heading(c) + label
            cur_src = c["source_id"]
            pf = (ch, c["source_file"])
            if pf not in part_files[-1]:
                part_files[-1].append(pf)
            cur.append(text); size += len(text.encode("utf-8"))
        parts.append(cur)
        names = []
        for i, p in enumerate(parts, 1):
            name = f"{num}_{cid}.md" if len(parts) == 1 else f"{num}_{cid}_p{i}.md"
            (PACK / name).write_text(head + "".join(p), encoding="utf-8")
            names.append(name)
        toc[cid] = {"name": reg["name"] + code, "files": names, "part_sources": part_files,
                    "chunks": len(chunks), "excluded": excluded}
        print(cid, names, len(chunks), "chunks")
    (SYSTEM / "work/w6b/grok_pack_toc.json").write_text(json.dumps(toc, ensure_ascii=False, indent=1), encoding="utf-8")
    mp = PACK / "00_MUC_LUC.md"
    m = mp.read_text(encoding="utf-8")
    cut = m.find(NL + "## 18_")
    m = (m if cut < 0 else m[:cut]).rstrip(NL) + NL
    for cid, t in toc.items():
        for f, srcs in zip(t["files"], t["part_sources"]):
            m += f"{NL}## {f}{NL}{t['name']} · Loại: GIÁO TRÌNH{NL}" + "".join(f"- Chương {ch} · {fn}{NL}" for ch, fn in srcs)
            if f == t["files"][0]:
                m += "".join(f"- Không có trong gói: {x}{NL}" for x in t["excluded"])
    mp.write_text(m, encoding="utf-8")


if __name__ == "__main__":
    main()
