# -*- coding: utf-8 -*-
"""V3 core regression comparator (plan spec 7.7).
Re-runs P2-P8 + pilot instrumentation eval scripts, collects their raw JSON
into reports/v3/run_<ts>/, compares against reports/v3/baseline/raw/.
Prints IDENTICAL or a diff list. Exit code 0 only when IDENTICAL.
"""
import json, os, re, shutil, subprocess, sys, time
from pathlib import Path

SYSTEM = Path(os.environ.get("HOC_ROOT", r"D:\Hoc")) / "_learning_system"
BASE = SYSTEM / "reports" / "v3" / "baseline" / "raw"
SCRIPTS = ["phase2_eval", "phase3_eval", "phase4_eval", "phase5_eval",
           "phase6_eval", "phase7_eval", "phase8_eval", "pilot_instrumentation_eval"]
# W6b R2 G01: fixed, independent catalogue of the raw outputs a certifying run must have (baseline AND this run).
REQUIRED_RAW = (
    "adaptive_adversarial_raw.json", "adaptive_benchmark_raw.json", "admission_benchmark_raw.json",
    "decision_benchmark_raw.json", "decision_naturalistic_raw.json", "diagnostic_benchmark_raw.json",
    "learner_state_benchmark_raw.json", "learning_policy_benchmark_raw.json", "pilot_instrumentation_raw.json",
    "retrieval_benchmark_raw.json",
)
IGNORE_KEYS = {"generated_at", "other_course_suggestions", "regulation_updates",
               "latency_s", "latency_mean_s", "latency_max_s", "timestamp", "ts", "elapsed_s"}
RE_ID = re.compile(r"\b(st|ev|sess|uuid)-[0-9a-f]{8,}\b")
RE_TS = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[^\"\s]*")


def norm(x):
    if isinstance(x, dict):
        return {k: norm(v) for k, v in x.items() if k not in IGNORE_KEYS and not k.endswith("_latency")}
    if isinstance(x, list):
        return [norm(v) for v in x]
    if isinstance(x, str):
        return RE_TS.sub("<ts>", RE_ID.sub(lambda m: m.group(1) + "-<id>", x))
    return x


def diff(a, b, path=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a: out.append(f"{path}/{k}: only in run")
            elif k not in b: out.append(f"{path}/{k}: only in baseline")
            else: out += diff(a[k], b[k], f"{path}/{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b): out.append(f"{path}: len {len(a)} vs {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)): out += diff(x, y, f"{path}[{i}]")
    elif a != b:
        out.append(f"{path}: baseline={str(a)[:80]!r} run={str(b)[:80]!r}")
    return out


def _run():
    ts = time.strftime("%Y%m%d_%H%M%S")
    run = SYSTEM / "reports" / "v3" / f"run_{ts}"
    (run / "raw").mkdir(parents=True)
    hist = SYSTEM / "reports"
    snap = {p.name: p.read_bytes() for p in hist.glob("*.md")}
    raw_snap = {p.name: p.read_bytes() for p in hist.glob("*_raw.json")}
    pilot = SYSTEM / "pilot"
    pilot_snap = {p: p.read_bytes() for p in pilot.rglob("*") if p.is_file()}
    baseline_names = sorted(b.name for b in BASE.glob("*.json"))
    if not baseline_names:
        sys.exit("DIFFERENT: baseline raw set is empty (cannot certify IDENTICAL)")
    for name in REQUIRED_RAW:  # W6b G01: no pre-existing raw may be mistaken for this run's output
        (hist / name).unlink(missing_ok=True)
    failed = []
    for s in SCRIPTS:
        command = [sys.executable, str(SYSTEM / "scripts" / f"{s}.py")]
        if '--external-candidate' in sys.argv:
            # Exercise the proposed external tier in each isolated suite process
            # without enabling it in the on-disk registry before G5 passes.
            bootstrap = ("import sys,runpy; sys.path.insert(0,sys.argv[1]); "
                         "from retrieval import courses as C; "
                         "[c.update(tier='retrieval') for c in C.load_registry()['courses'] if c['id']=='external']; "
                         "runpy.run_path(sys.argv[2],run_name='__main__')")
            command = [sys.executable, '-c', bootstrap, str(SYSTEM), str(SYSTEM / 'scripts' / f'{s}.py')]
        r = subprocess.run(command, capture_output=True, text=True,
                           encoding="utf-8", env={**os.environ, "HOC_ROOT": str(SYSTEM.parent)})
        (run / f"{s}.stdout.txt").write_text(r.stdout + r.stderr, encoding="utf-8")
        if r.returncode != 0:
            print(f"SCRIPT_FAIL {s} rc={r.returncode}")
            failed.append(s)
    for p in snap:  # restore historical md reports overwritten by the eval scripts
        (hist / p).write_bytes(snap[p])
    for p, data in pilot_snap.items():  # eval scripts append to pilot logs; restore (frozen)
        p.write_bytes(data)
    diffs = [f"SCRIPT_FAIL {x}" for x in failed]
    req = set(REQUIRED_RAW)
    have_base = {b.name for b in BASE.glob("*.json")}
    for n in sorted(req - have_base): diffs.append(f"{n}: required baseline missing")
    for n in sorted(have_base - req): diffs.append(f"{n}: baseline not in required catalogue")
    # required raws were deleted before the run, so any present now was written by it; other pre-existing raws are excluded
    fresh = {p.name for p in hist.glob("*_raw.json")} - (set(raw_snap) - req)
    for n in sorted(req - fresh): diffs.append(f"{n}: raw not written in this run")
    for n in sorted(fresh - req): diffs.append(f"{n}: unexpected raw written in this run")
    for b in sorted(BASE.glob("*.json")):
        raw = hist / b.name
        if not raw.exists():
            diffs.append(f"{b.name}: missing in run"); continue
        shutil.copy2(raw, run / "raw" / b.name)
        d = diff(norm(json.loads(b.read_text(encoding="utf-8"))), norm(json.loads(raw.read_text(encoding="utf-8"))), b.stem)
        diffs += d
    (run / "diff.txt").write_text("\n".join(diffs) or "IDENTICAL", encoding="utf-8")
    # W6b: the run's raw JSON is now kept in run/raw; restore the historical reports/*_raw.json
    # so a regression run never leaves tracked history modified (they were showing up in commits).
    for name, data in raw_snap.items():
        (hist / name).write_bytes(data)
    if diffs:
        print("DIFFERENT", len(diffs)); print("\n".join(diffs[:60])); sys.exit(1)
    print("IDENTICAL", run)


def main():
    # W6b G01: whatever happens (exception, sys.exit, Ctrl+C) the historical reports/*_raw.json are put back.
    hist = SYSTEM / "reports"
    saved = {p.name: p.read_bytes() for p in hist.glob("*_raw.json")}
    try:
        _run()
    finally:
        for name, data in saved.items():
            (hist / name).write_bytes(data)


if __name__ == "__main__":
    main()
