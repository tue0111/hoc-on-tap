# Informational: pairwise 8-shingle overlap between every pair of extracted KTTC3 documents
# (spec 7.3 has no unit-script pairs here: no _nguon folder). Writes work/<C>/pairwise_overlap.json only.
import json, sys, itertools
from pathlib import Path
SYS = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(SYS))
from scripts.v3_dedupe import norm_tokens, shingles
C = "ke-toan-tai-chinh-3"
docs = [json.loads(l) for l in (SYS / "data/normalized" / f"{C}.documents.jsonl").open(encoding="utf-8")]
docs = [d for d in docs if d["extract_ok"]]
S = {d["source_id"]: shingles(norm_tokens(d["text"])) for d in docs}
out = []
for a, b in itertools.combinations(S, 2):
    i = len(S[a] & S[b])
    if not i: continue
    out.append({"a": a, "b": b, "cov_a": round(i / len(S[a]), 4), "cov_b": round(i / len(S[b]), 4), "shared": i})
out.sort(key=lambda x: -max(x["cov_a"], x["cov_b"]))
(SYS / "work" / C / "pairwise_overlap.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
for r in out[:12]: print(r)
