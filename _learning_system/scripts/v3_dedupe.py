# -*- coding: utf-8 -*-
"""V3 dedupe analysis (plan spec 7.3). usage: python scripts/v3_dedupe.py --course C
Writes reports/v3/C_dedupe.json and updates combined_duplicate / index_include in C.documents.jsonl.
Mid-band chapters (0.50 < cov < 0.85) get chunk-level dup_group assigned later by v3_build_partition.py.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from retrieval import courses as C
from retrieval.config import SYSTEM
from retrieval.textutil import fold, tokenize

PAGE_RE = re.compile(r"^-{3,}\s*PAGE\s*\d+\s*-{3,}$", re.I)
HI, LO = 0.85, 0.50


def norm_tokens(text: str) -> list[str]:
    lines = []
    for ln in text.splitlines():
        ln = re.sub(r"\s+", " ", fold(ln)).strip()
        if PAGE_RE.match(ln) or len(ln) < 4:
            continue
        lines.append(ln)
    return tokenize(" ".join(lines))


def shingles(toks: list[str], n: int = 8) -> set:
    return {" ".join(toks[i:i + n]) for i in range(max(len(toks) - n + 1, 0))}


def compare(upper: dict, lowers: list[dict]) -> dict:
    s_up = shingles(norm_tokens(upper["text"]))
    s_lo = set()
    for d in lowers:
        s_lo |= shingles(norm_tokens(d["text"]))
    inter = s_up & s_lo
    cov = len(inter) / len(s_up) if s_up else 0.0
    back = len(inter) / len(s_lo) if s_lo else 0.0
    if cov >= HI: dec = "combined_duplicate"
    elif cov <= LO: dec = "both_canonical"
    else: dec = "REVIEW" if back < 0.5 else "both_indexed_chunk_dedupe"
    return {"upper": upper["source_id"], "upper_file": upper["source_file"], "lowers": [d["source_id"] for d in lowers],
            "cov": round(cov, 4), "back": round(back, 4), "decision": dec,
            "shingles_upper": len(s_up), "shingles_lower": len(s_lo)}


def is_coursewide_slide(doc: dict) -> bool:
    """Wave 3 combined-slide candidates such as Slide.pdf / Slide <course>.pdf."""
    if doc.get("chapter") is not None or not str(doc.get("source_file", "")).lower().endswith(".pdf"):
        return False
    stem = fold(Path(doc["source_file"]).stem).replace(" ", "")
    return stem.startswith("slide")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--course", required=True)
    cid = ap.parse_args().course
    p = C.partition_paths(cid)
    docs = [json.loads(l) for l in p["documents"].open(encoding="utf-8")]
    ok = [d for d in docs if d["extract_ok"] and not d["learner_material"]]
    units = [d for d in ok if d["unit_script"]]
    pairs = []
    # (a) chapter-level docs vs unit scripts of the same chapter
    chap_docs = [d for d in ok if not d["unit_script"] and d["chapter"] is not None and d["source_type"] not in ("exam", "summary", "exercise", "solution")]
    for d in chap_docs:
        lows = [u for u in units if u["chapter"] == d["chapter"]]
        if lows:
            r = compare(d, lows); r["scope"] = f"chapter {d['chapter']}"; pairs.append(r)
    # (b) course-wide combined docs (override says combined) vs everything else
    for d in ok:
        if "combined" in str(d["content_role"]):
            lows = [x for x in ok if x["source_id"] != d["source_id"] and "combined" not in str(x["content_role"])
                    and x["source_type"] not in ("exam", "summary")]
            if lows:
                r = compare(d, lows); r["scope"] = "course-wide combined"; pairs.append(r)
    # (c) Wave 3 course-wide slide PDFs vs per-chapter files.  These files do not
    # always carry a combined override, so detect the documented filename shape.
    for d in ok:
        if is_coursewide_slide(d) and "combined" not in str(d["content_role"]):
            lows = [x for x in ok if x["source_id"] != d["source_id"] and x.get("chapter") is not None
                    and "combined" not in str(x["content_role"])
                    and x["source_type"] not in ("exam", "summary")]
            if lows:
                r = compare(d, lows); r["scope"] = "course-wide slides"; pairs.append(r)
    byid = {d["source_id"]: d for d in docs}
    mid = []
    for r in pairs:
        if r["decision"] == "combined_duplicate":
            d = byid[r["upper"]]; d["combined_duplicate"] = True; d["index_include"] = False
        elif r["decision"] == "both_indexed_chunk_dedupe":
            mid.append(r["scope"])
    review = [r for r in pairs if r["decision"] == "REVIEW"]
    with p["documents"].open("w", encoding="utf-8") as f:
        for d in docs: f.write(json.dumps(d, ensure_ascii=False) + "\n")
    out = SYSTEM / "reports" / "v3" / f"{cid}_dedupe.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"course_id": cid, "thresholds": {"dup": HI, "distinct": LO}, "pairs": pairs,
                               "mid_band_scopes": mid, "REVIEW": [r["upper"] for r in review]}, ensure_ascii=False, indent=2), encoding="utf-8")
    for r in pairs: print(f"{r['scope']:22} {r['upper']} {r['upper_file'][:24]:24} cov={r['cov']} back={r['back']} -> {r['decision']}")
    print("REVIEW:", [r["upper"] for r in review])
    if review: sys.exit(2)


if __name__ == "__main__":
    main()
