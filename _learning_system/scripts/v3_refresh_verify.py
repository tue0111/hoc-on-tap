"""Prove that no-op refresh and the approved RAM simulation do not mutate data."""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from retrieval.config import SYSTEM, SOURCE_ROOT


def snapshot():
    paths = [SYSTEM / 'inventory/files.json']
    for folder in ('data', 'evals', 'learner', 'pilot/events', 'pilot/sessions', 'pilot/corrections', 'pilot/feedback'):
        paths.extend(p for p in (SYSTEM / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    return {p.relative_to(SYSTEM).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def main():
    before = snapshot()
    commands = [('v3_refresh.py', '--plan'), ('v3_refresh.py', '--apply'), ('v3_refresh_selftest.py',)]
    for command in commands:
        subprocess.run([sys.executable, '-X', 'utf8', str(SYSTEM / 'scripts' / command[0]), *command[1:]],
                       cwd=SYSTEM, env={**os.environ, 'HOC_ROOT': str(SOURCE_ROOT)}, check=True)
    after = snapshot()
    drift = [k for k in set(before) | set(after) if before.get(k) != after.get(k)]
    frozen = json.loads((SYSTEM / 'evals/v3/FROZEN.json').read_text(encoding='utf-8'))
    frozen_ok = all(hashlib.sha256((SYSTEM / r['file']).read_bytes()).hexdigest() == r['sha256'] for r in frozen.values())
    report = {'tracked_files': len(before), 'byte_identical': not drift, 'drift': drift,
              'frozen_v3_suites': len(frozen), 'frozen_hashes_match': frozen_ok,
              'scope': 'inventory, data, evals, learner state and pilot event/session/correction/feedback files',
              'all_pass': not drift and frozen_ok}
    (SYSTEM / 'reports/v3/refresh_noop_integrity.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))
    if not report['all_pass']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
