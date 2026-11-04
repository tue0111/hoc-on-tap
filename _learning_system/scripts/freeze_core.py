# -*- coding: utf-8 -*-
from __future__ import annotations
import json
import sys
from pathlib import Path
import os as _os
_SYS = Path(_os.environ.get("HOC_ROOT", r"D:\Hoc")) / "_learning_system"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from study.freeze import build_manifest
from study.integrity import BLOCK


def main():
    import hashlib
    import yaml
    dest = _SYS / 'pilot' / 'core_freeze_manifest.json'
    old = json.loads(dest.read_text(encoding='utf-8')) if dest.exists() else None
    original = dest.read_bytes() if dest.exists() else None
    # Never re-baseline changed suites by overwriting the old manifest.
    if old:
        for rel, record in old['frozen_suites'].items():
            if hashlib.sha256((_SYS / rel).read_bytes()).hexdigest() != record['sha256']:
                raise RuntimeError('Frozen suite changed: ' + rel)
    man = build_manifest()
    if man['source_integrity']['status'] == BLOCK:
        print(json.dumps(man['source_integrity'], indent=2))
        sys.exit(2)
    if old and man['frozen_suites'] != old['frozen_suites']:
        raise RuntimeError('Frozen suite manifest changed')
    registry_path = _SYS / 'curriculum/course_registry.yaml'
    if registry_path.exists():
        courses = yaml.safe_load(registry_path.read_text(encoding='utf-8'))['courses']
        man['v3_partitions'] = {}
        for course in courses:
            meta_path = _SYS / 'data/indexes/3.0.0' / course['id'] / 'meta.json'
            if not meta_path.exists():
                continue
            meta = json.loads(meta_path.read_text(encoding='utf-8'))
            man['v3_partitions'][course['id']] = {
                'tier': course['tier'], 'chunk_count': meta['chunk_count'],
                'source_hashes_count': len(meta['source_hashes']),
                'meta_sha256': hashlib.sha256(meta_path.read_bytes()).hexdigest(),
            }
    if (dest.read_bytes() if dest.exists() else None) != original:
        raise RuntimeError('Freeze manifest changed during verification')
    dest.write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({"status": man["source_integrity"]["status"], "checked": man["source_integrity"]["checked"], "path": str((_SYS / "pilot" / "core_freeze_manifest.json"))}, indent=2))
    if man["source_integrity"]["status"] == BLOCK:
        sys.exit(2)


if __name__ == "__main__":
    main()
