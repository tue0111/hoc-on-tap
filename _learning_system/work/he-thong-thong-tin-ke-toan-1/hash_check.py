# -*- coding: utf-8 -*-
"""6.1 hash check (read-only) for he-thong-thong-tin-ke-toan-1."""
import hashlib, json
from pathlib import Path

CID = "he-thong-thong-tin-ke-toan-1"
ROOT = Path(r"D:\Hoc")
SYS = ROOT / "_learning_system"
rows = json.load(open(SYS / "inventory" / "files.json", encoding="utf-8"))
rs = [r for r in rows if r.get("course_id") == CID]
bad, out = [], []
for r in rs:
    p = ROOT / r["relative_path"]
    if not p.exists():
        bad.append(("missing", r["source_id"])); continue
    h = hashlib.sha256(p.read_bytes()).hexdigest(); s = p.stat().st_size
    ok = h == r["sha256"] and s == r["size_bytes"]
    out.append({"source_id": r["source_id"], "relative_path": r["relative_path"], "sha256": h, "size": s, "match": ok})
    if not ok: bad.append(("mismatch", r["source_id"]))
inv = {r["relative_path"] for r in rs}
extra = [p.relative_to(ROOT).as_posix() for p in (ROOT / "Hệ thống thông tin kế toán 1").rglob("*") if p.is_file()]
extra = [e for e in extra if e not in inv]
json.dump({"checked": len(out), "bad": bad, "not_in_inventory": extra, "rows": out},
          open(SYS / "work" / CID / "hash_check.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("checked", len(out), "bad", bad, "not_in_inventory", extra)
