"""Wave 6 staged refresh. No writes to course folders; no deletes anywhere.

--plan saves a hash-bound plan; --apply PLAN builds an isolated candidate before
publishing. Unique content requires a recorded semantic/citation review. Missing
sources and all core additions/changes stop without changing live inventory/indexes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from contextlib import contextmanager
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import yaml
from retrieval.config import SYSTEM, SOURCE_ROOT, SLICE_COURSE_IDS
from scripts.v3_inventory import active_records
from scripts.build_inventory import COURSE_IDS, ARTIFACT_PATH_RE, classify

# Plan 0.6 supported source formats; anything else is inventoried with index_include: false (W6b).
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.pptx', '.txt', '.md', '.xlsx'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def safe_relative(rel):
    p = PurePosixPath(rel.replace('\\', '/'))
    if p.is_absolute() or '..' in p.parts or ':' in str(p) or not p.parts or p.parts[0] == '_learning_system':
        raise ValueError('Unsafe source path: ' + rel)
    return p.as_posix()


def listing(root):
    rows = []
    for folder in sorted(root.iterdir()):
        # W6b: D:\Hoc is also a git repo; skip system/tooling entries (.git, _grok_pack, _learning_system)
        # and loose files at the root (README.md, .gitignore). Course material lives only in course folders.
        if folder.name.startswith(('.', '_')) or not folder.is_dir():
            continue
        if folder.is_symlink() or (hasattr(folder, 'is_junction') and folder.is_junction()):
            raise ValueError('Reparse source root: ' + folder.name)
        if folder.is_dir():
            for base, dirs, files in os.walk(folder, followlinks=False):
                for name in dirs + files:
                    p = Path(base) / name
                    if p.is_symlink() or (hasattr(p, 'is_junction') and p.is_junction()):
                        raise ValueError('Reparse source: ' + str(p))
                for name in sorted(files):
                    p = Path(base) / name
                    s = p.stat()
                    rows.append({'relative_path': p.relative_to(root).as_posix(), 'size_bytes': s.st_size, 'mtime_ns': s.st_mtime_ns})
        elif folder.is_file():
            s = folder.stat()
            rows.append({'relative_path': folder.name, 'size_bytes': s.st_size, 'mtime_ns': s.st_mtime_ns})
    return sorted(rows, key=lambda r: r['relative_path'])


def compare(rows, inventory):
    old = {r['relative_path'].casefold(): r for r in active_records(inventory)}
    current = {safe_relative(r['relative_path']).casefold(): r for r in rows}
    if len(current) != len(rows):
        raise ValueError('Ambiguous listing paths')
    return {'NEW': [r for k, r in current.items() if k not in old],
            'CHANGED': [{**r, 'supersedes': old[k]['source_id']} for k, r in current.items() if k in old and r['size_bytes'] != old[k]['size_bytes']],
            'MISSING': [r for k, r in old.items() if k not in current]}


def classify_source(rel, first_page='', previous=None):
    rel = safe_relative(rel)
    folder, name = rel.split('/')[0], PurePosixPath(rel).name
    cid = COURSE_IDS.get(folder)
    if not cid:
        raise ValueError('Unknown course folder: ' + folder)
    tmp = bool(ARTIFACT_PATH_RE.search(rel)) or bool(re.search(r'preview|proxy', name, re.I))
    learner = bool(re.search(r'claude outputs|nguy[eễ]n\s*đ?[uứ]c\s*tu[eệ]|nguyenductue|họ\s*tên\s*sinh\s*viên|s[oổ][ _]tay', rel + '\n' + first_page, re.I))
    role = classify(rel, name, PurePosixPath(rel).suffix.lower())['source_role']
    if '/_nguon/' in '/' + rel:
        role = 'lecture_note'
    if previous:
        role = previous.get('content_role') or previous.get('source_role') or role
        learner = learner or role == 'learner_material'
    return {'course_id': cid, 'source_role': 'learner_material' if learner else role,
            'partition': 'excluded' if tmp else ('learner-notes' if learner else cid),
            'tmp_artifact': tmp, 'classification_evidence_status': 'INFERRED',
            'classification_reason': 'Wave 6 filename/path + extracted first-page rules; inherited role on revision'}


def append_records(inventory, staged):
    """Pure append; old rows are neither renumbered nor rewritten."""
    result = list(inventory)
    serial = max((int(r['source_id'].split('-')[1]) for r in result), default=0)
    for entry in staged:
        serial += 1
        rel = safe_relative(entry['relative_path'])
        result.append({k: v for k, v in {**entry, 'source_id': f'src-{serial:04d}',
                      'filename': PurePosixPath(rel).name, 'extension': PurePosixPath(rel).suffix.lower(),
                      'course_folder': rel.split('/')[0], 'notes': ['added_in_v3_refresh']}.items()
                       if k not in ('staged_path', 'mtime_ns')})
    active_records(result)
    return result


def guard(delta):
    touched = delta['NEW'] + delta['CHANGED'] + delta['MISSING']
    if any(COURSE_IDS.get(r['relative_path'].split('/')[0]) in SLICE_COURSE_IDS for r in touched):
        raise ValueError('OPUS_ONLY: core source added, changed or missing; index 2.0.0 untouched')
    if delta['MISSING']:
        raise ValueError('MISSING sources: no deletion or silent inventory retirement')


def core_integrity():
    from study.integrity import verify_sources
    checked = verify_sources()
    if not checked['ok']:
        raise ValueError('OPUS_ONLY: core hash integrity failed (including same-size edits)')


@contextmanager
def refresh_lock():
    path = SYSTEM / 'work/refresh/refresh.lock'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+b') as handle:
        if path.stat().st_size == 0:
            handle.write(b'0')
            handle.flush()
        handle.seek(0)
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == 'nt':
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


def plan():
    inv_path = SYSTEM / 'inventory/files.json'
    inv = read_json(inv_path)
    rows = listing(SOURCE_ROOT)
    delta = compare(rows, inv)
    tag = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')
    dest = SYSTEM / 'work/refresh' / tag
    dest.mkdir(parents=True)
    result = {'version': 1, 'created_at': tag, 'inventory_sha256': digest(inv_path.read_bytes()),
              'delta': delta, 'staged': [], 'blocked': None,
              'detection_contract': 'relative_path + size; same-size edits are NOT detected by this scan'}
    write_json(SYSTEM / 'work/listing.json', rows)
    new_courses = sorted({r['relative_path'].split('/')[0] for r in delta['NEW']} - set(COURSE_IDS))
    result['new_courses'] = new_courses
    try:
        if new_courses:
            # W6b: a new course needs registry/parser/concept judgment work, which refresh cannot do.
            raise ValueError('NEW_COURSE: ' + ', '.join(new_courses) + '. Không nạp tự động. Làm theo checklist '
                             'reports/v3/PLAN_W6B_MON_MOI.md (Pha A: COURSE_IDS + course_registry + parser; '
                             'Pha B: playbook mục 6; Pha C: gộp, gate, _grok_pack), rồi chạy lại --plan.')
        guard(delta)
        core_integrity()
        for entry in delta['NEW'] + delta['CHANGED']:
            rel = safe_relative(entry['relative_path'])
            src = SOURCE_ROOT / rel
            before = src.stat()
            data = src.read_bytes()
            after = src.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns) or len(data) != entry['size_bytes'] or after.st_mtime_ns != entry['mtime_ns']:
                raise ValueError('Source drift during staging: ' + rel)
            target = dest / 'staged' / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            result['staged'].append({**entry, 'sha256': digest(data), 'staged_path': target.relative_to(SYSTEM).as_posix()})
    except ValueError as exc:
        result['blocked'] = str(exc)
    write_json(dest / 'plan.json', result)
    write_json(SYSTEM / 'work/refresh/latest.json', {'plan': str(dest / 'plan.json')})
    report(result, 'BLOCKED' if result['blocked'] else 'PLANNED', dest / 'plan.json')
    print(json.dumps({'plan': str(dest / 'plan.json'), 'counts': {k: len(v) for k, v in delta.items()}, 'blocked': result['blocked']}, ensure_ascii=False))
    return 2 if result['blocked'] else 0


def report(data, status, path, detail=''):
    date = datetime.now().strftime('%Y%m%d')
    dest = SYSTEM / f'reports/v3/refresh_{date}.md'
    existing = dest.read_text(encoding='utf-8') if dest.exists() else '# Wave 6 refresh log\n'
    counts = {k: len(v) for k, v in data['delta'].items()}
    dest.write_text(existing + f'\n## {datetime.now(timezone.utc).isoformat()} — {status}\n\nPlan: `{path}`\n\nCounts: `{counts}`\n\n{detail or data.get("blocked") or "No source files modified."}\n', encoding='utf-8')


def command(root, script, *args):
    result = subprocess.run([sys.executable, '-X', 'utf8', str(root / '_learning_system/scripts' / script), *args],
                            cwd=root / '_learning_system', env={**os.environ, 'HOC_ROOT': str(root), 'PYTHONIOENCODING': 'utf-8'},
                            capture_output=True, text=True, encoding='utf-8')
    log = root / '_learning_system/reports/v3' / f'refresh_{Path(script).stem}.log'
    log.write_text(result.stdout + result.stderr, encoding='utf-8')
    if result.returncode or 'SCRIPT_FAIL' in result.stdout or 'Traceback' in result.stderr:
        raise ValueError('Candidate command failed: ' + script + '; ' + str(log))


def apply(plan_path, review_path=None):
    plan_path = plan_path.resolve()
    if not plan_path.is_relative_to((SYSTEM / 'work/refresh').resolve()):
        raise ValueError('Plan must be under workspace work/refresh')
    p = read_json(plan_path)
    guard(p['delta'])
    core_integrity()
    if p['blocked']:
        raise ValueError(p['blocked'])
    inv_path = SYSTEM / 'inventory/files.json'
    if digest(inv_path.read_bytes()) != p['inventory_sha256']:
        raise ValueError('Inventory drift; make a new plan')
    inv = read_json(inv_path)
    current = compare(listing(SOURCE_ROOT), inv)
    if current != p['delta']:
        raise ValueError('Source listing/mtime drift; make a new plan')
    if not p['staged']:
        report(p, 'NOOP', plan_path, '0 NEW / 0 CHANGED; inventory and all indexes left byte-identical.')
        print('NOOP: inventory/indexes unchanged')
        return 0
    # Build only in an isolated candidate; no live inventory or index is changed
    # until extraction, semantic review, all gates and regression have passed.
    root = plan_path.parent / ('candidate_' + datetime.now().strftime('%H%M%S_%f'))
    cs = root / '_learning_system'
    cs.mkdir(parents=True)
    before = {}
    folders = ('scripts', 'retrieval', 'research', 'curriculum', 'data', 'inventory', 'evals',
               'diagnostic', 'decision', 'adaptive', 'admission', 'mastery', 'learning_policy',
               'study', 'learner', 'pilot', 'schemas', 'autopilot', 'reports')
    for folder in folders:
        origin = SYSTEM / folder
        if origin.exists():
            shutil.copytree(origin, cs / folder, ignore=shutil.ignore_patterns('__pycache__'))
            for f in origin.rglob('*'):
                if f.is_file() and '__pycache__' not in f.parts:
                    before[f.relative_to(SYSTEM).as_posix()] = (f.stat().st_mtime_ns, digest(f.read_bytes()))
    if (SYSTEM / 'work/v3_deps').exists():
        shutil.copytree(SYSTEM / 'work/v3_deps', cs / 'work/v3_deps')
    ov = yaml.safe_load((cs / 'curriculum/source_registry_overrides.yaml').read_text(encoding='utf-8'))
    overrides = {r['source_id']: r for r in ov.get('overrides', [])}
    active = active_records(inv)
    by_id = {r['source_id']: r for r in active}
    classified = []
    from scripts.v3_extract_learner_notes import extract_one
    for entry in p['staged']:
        src = SOURCE_ROOT / safe_relative(entry['relative_path'])
        staged = (SYSTEM / entry['staged_path']).resolve()
        if not staged.is_relative_to(plan_path.parent.resolve()):
            raise ValueError('Unsafe staged path')
        data = staged.read_bytes()
        if digest(data) != entry['sha256'] or digest(src.read_bytes()) != entry['sha256']:
            raise ValueError('Source/staging hash drift')
        old = by_id.get(entry.get('supersedes'))
        previous = {**old, **overrides.get(old['source_id'], {})} if old else None
        initial = classify_source(entry['relative_path'], previous=previous)
        unsupported = staged.suffix.lower() not in SUPPORTED_EXTENSIONS
        if initial['tmp_artifact'] or unsupported:
            # W6b: unsupported formats (.xls/.xlsm/...) are inventoried, never indexed, never converted.
            extracted = {'ok': True, 'pages': []}
        else:
            extracted = extract_one(staged, staged.suffix.lower())
            if not extracted['ok']:
                raise ValueError('Unsupported/unreadable new source: ' + entry['relative_path'])
        first = (extracted.get('pages') or [{}])[0].get('text', '')
        classified.append({**entry, **classify_source(entry['relative_path'], first, previous)})
    new_inv = append_records(inv, classified)
    new_rows = new_inv[len(inv):]
    affected = sorted({r['partition'] for r in new_rows if r['partition'] != 'excluded'})
    for row in new_rows:
        old = by_id.get(row.get('supersedes'))
        if old:
            old_rule = overrides.get(old['source_id'], {})
            old_partition = ('learner-notes' if old_rule.get('content_role', old.get('source_role')) == 'learner_material'
                             else old['course_id'])
            if old_partition not in affected and not old.get('tmp_artifact'):
                affected.append(old_partition)
    affected.sort()
    # Core is only copied for integrity/regression; it is never rebuilt.
    copy_courses = {r['course_id'] for r in new_rows} | set(SLICE_COURSE_IDS)
    for row in active_records(new_inv):
        if row['course_id'] in copy_courses or 'learner-notes' in affected:
            src = SOURCE_ROOT / safe_relative(row['relative_path'])
            data = src.read_bytes()
            if digest(data) != row['sha256']:
                raise ValueError('Affected/core source integrity failed: ' + row['source_id'])
            dst = root / row['relative_path']
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)
    write_json(cs / 'inventory/files.json', new_inv)
    for row in new_rows:
        inherited = dict(overrides.get(row.get('supersedes'), {}))
        ov.setdefault('overrides', []).append({**inherited, 'source_id': row['source_id'], 'relative_path': row['relative_path'],
                                              'content_role': row['source_role'], 'partition': row['partition'],
                                              'evidence_status': 'INFERRED', 'note': 'Wave 6 classification; see refresh plan/review'})
        if PurePosixPath(row['relative_path']).suffix.lower() not in SUPPORTED_EXTENSIONS:
            ov['overrides'][-1].update(index_include=False, exclusion_reason='unsupported_extension')
        if row['tmp_artifact']:
            ov.setdefault('tmp_artifacts_not_curriculum', []).append(row['source_id'])
    (cs / 'curriculum/source_registry_overrides.yaml').write_text(yaml.safe_dump(ov, allow_unicode=True, sort_keys=False), encoding='utf-8')
    for cid in affected:
        if cid == 'learner-notes':
            command(root, 'v3_extract_learner_notes.py')
        else:
            command(root, 'v3_extract_course.py', '--course', cid)
            coverage = read_json(cs / f'data/normalized/{cid}.coverage.json')
            if coverage['errors'] or coverage['page_count_mismatch'] or coverage['UNPARSED']:
                raise ValueError('Extraction gate failed: ' + cid)
            command(root, 'v3_dedupe.py', '--course', cid)
            (cs / 'work' / cid).mkdir(parents=True, exist_ok=True)
            command(root, 'v3_concept_candidates.py', '--course', cid)
    # Exact copies introduce no new concepts/citations. Unique material requires
    # a human/agent review bound to source hashes, not an invented automatic judgment.
    known = {r['sha256'] for r in inv}
    unique = [r for r in new_rows if r['sha256'] not in known and not r['tmp_artifact']]
    review = read_json(review_path) if review_path else {}
    if not unique and review:
        raise ValueError('Review supplied without unique sources; make a separate reviewed update')
    if unique:
        expected = {r['source_id']: r['sha256'] for r in unique}
        if review.get('source_hashes') != expected or not review.get('concepts_reviewed') or not review.get('citations_reviewed'):
            write_json(plan_path.parent / 'review_required.json', {'source_hashes': expected, 'candidate': str(cs),
                       'required': 'Review concept candidates + new citation official status; supply review JSON and provenance-backed concept/regulation files.'})
            report(p, 'REVIEW_REQUIRED', plan_path, 'Candidate extracted; live inventory/indexes unchanged. See review_required.json.')
            return 2
        for rel, sha in review.get('files', {}).items():
            relpath = PurePosixPath(rel)
            allowed = (rel in {f'curriculum/concepts/{cid}.yaml' for cid in affected if cid not in SLICE_COURSE_IDS}
                       or rel.startswith('research/regulations/'))
            if not allowed or '..' in relpath.parts or ':' in rel or '\\' in rel or relpath.is_absolute():
                raise ValueError('Review file out of scope')
            source = review_path.parent / rel
            if digest(source.read_bytes()) != sha:
                raise ValueError('Review file hash mismatch')
            (cs / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, cs / rel)
    for cid in affected:
        if cid == 'learner-notes':
            command(root, 'v3_build_learner_notes.py')
            command(root, 'v3_eval_learner_notes.py', '--tag', '_refresh')
        else:
            command(root, 'v3_validate_concepts.py', '--course', cid)
            command(root, 'v3_build_partition.py', '--course', cid)
            command(root, 'v3_eval_course.py', '--course', cid, '--tag', '_refresh')
            evaluation = read_json(cs / f'reports/v3/{cid}_eval_refresh.json')
            gates = dict(evaluation['gates'])
            if cid == 'ke-toan-chi-phi':
                kept = [r for r in evaluation['results'] if r['id'] not in {'kp-t01', 'kp-t02', 'kp-t03'}]
                gates['topic_owner'] = all(r['pass'] for r in kept if r['category'] == 'topic_owner')
                write_json(cs / 'reports/v3/refresh_d2_waiver.json', {'label': 'D2 waiver', 'excluded': ['kp-t01','kp-t02','kp-t03'], 'gates': gates})
            if not all(gates.values()):
                raise ValueError('Frozen course gate failed: ' + cid)
    command(root, 'v3_harvest_citations.py')
    from research.citations import slug
    record_changes = set(r for r in review.get('files', {}) if r.startswith('research/regulations/'))
    for citation in read_json(cs / 'research/curriculum_citations.json'):
        rel = 'research/regulations/' + slug(citation['ref_normalized']) + '.yaml'
        record_path = cs / rel
        if not record_path.exists():
            raise ValueError('Citation requires official-source review/explicit unknown record: ' + citation['ref_normalized'])
        raw = record_path.read_text(encoding='utf-8')
        rec = yaml.safe_load(raw)
        updated = {**rec, 'cited_in_courses': citation['courses'], 'curriculum_occurrences': citation['occurrences'], 'variants': citation['variants']}
        if updated != rec:
            record_path.write_text(yaml.safe_dump(updated, allow_unicode=True, sort_keys=False), encoding='utf-8')
            record_changes.add(rel)
    external_changed = bool(record_changes)
    if external_changed:
        command(root, 'v3_build_external.py', '--from-records')
    command(root, 'v3_eval_external.py')
    # A new partition corpus can affect off-outline comparison in other courses.
    registry = yaml.safe_load((cs / 'curriculum/course_registry.yaml').read_text(encoding='utf-8'))
    for course in registry['courses']:
        cid = course['id']
        if course['tier'] != 'retrieval' or cid in affected or cid in {'learner-notes', 'external'}:
            continue
        command(root, 'v3_eval_course.py', '--course', cid, '--tag', '_refresh_unaffected')
        # Compare against a live pre-refresh run, not a fabricated or re-frozen suite.
        command(SOURCE_ROOT, 'v3_eval_course.py', '--course', cid, '--tag', '_refresh_before')
        old = read_json(SYSTEM / f'reports/v3/{cid}_eval_refresh_before.json')['results']
        new = read_json(cs / f'reports/v3/{cid}_eval_refresh_unaffected.json')['results']
        if old != new:
            raise ValueError('Non-target course output changed: ' + cid)
    command(root, 'v3_regression.py')
    latest_run = max((cs / 'reports/v3').glob('run_*'), key=lambda p: p.name)
    if (latest_run / 'diff.txt').read_text().strip() != 'IDENTICAL':
        raise ValueError('Core regression differs')
    command(root, 'freeze_core.py')
    for cid in affected:
        manifest_path = cs / f'curriculum/course_manifests/{cid}.yaml'
        if manifest_path.exists():
            manifest = yaml.safe_load(manifest_path.read_text(encoding='utf-8'))
            coverage = read_json(cs / f'data/normalized/{cid}.coverage.json')
            meta = read_json(cs / f'data/indexes/3.0.0/{cid}/meta.json')
            manifest.setdefault('v3', {}).update(chunk_count=meta['chunk_count'], last_refresh=p['created_at'],
                refresh_document_count=coverage['document_count'], refresh_page_count=coverage['page_count'])
            manifest_path.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding='utf-8')
    # Publish an explicit allowlist only. No core, eval, learner-state or pilot logs.
    publish = ['inventory/files.json', 'curriculum/source_registry_overrides.yaml',
               'research/curriculum_citations.json', 'pilot/core_freeze_manifest.json']
    for cid in affected:
        if (cs / f'curriculum/course_manifests/{cid}.yaml').exists():
            publish.append(f'curriculum/course_manifests/{cid}.yaml')
        publish += [p.relative_to(cs).as_posix() for p in (cs / 'data/normalized').glob(cid + '.*')]
        publish += [p.relative_to(cs).as_posix() for p in (cs / 'data/chunks').glob(cid + '.*')]
        publish += [p.relative_to(cs).as_posix() for p in (cs / 'data/indexes/3.0.0' / cid).rglob('*') if p.is_file()]
        publish += [p.relative_to(cs).as_posix() for p in (cs / 'reports/v3').glob(cid + '*') if p.is_file()]
    publish += list(review.get('files', {}))
    publish += sorted(record_changes)
    if (cs / 'reports/v3/refresh_d2_waiver.json').exists():
        publish.append('reports/v3/refresh_d2_waiver.json')
    if external_changed:
        publish.append('reports/v3/external_build.json')
        publish += [p.relative_to(cs).as_posix() for p in (cs / 'data/chunks').glob('external.*')]
        publish += [p.relative_to(cs).as_posix() for p in (cs / 'data/indexes/3.0.0/external').rglob('*') if p.is_file()]
    publish = sorted(set(publish))
    publish = [rel for rel in publish if not (SYSTEM / rel).exists()
               or digest((SYSTEM / rel).read_bytes()) != digest((cs / rel).read_bytes())]
    for rel, original_state in before.items():
        if rel.startswith('reports/'):
            continue  # Non-target diagnostic runs intentionally add/refresh reports.
        live = SYSTEM / rel
        state = (live.stat().st_mtime_ns, digest(live.read_bytes())) if live.exists() else None
        if state != original_state:
            raise ValueError('Live dependency changed during candidate build: ' + rel)
    for rel in publish:
        target = SYSTEM / rel
        state = (target.stat().st_mtime_ns, digest(target.read_bytes())) if target.exists() else None
        if state != before.get(rel):
            raise ValueError('Live mtime/content drift before publish: ' + rel)
    for entry in p['staged']:
        if digest((SOURCE_ROOT / entry['relative_path']).read_bytes()) != entry['sha256']:
            raise ValueError('Source drift before publish')
    # Backup every overwritten file. Candidate and backup are retained, never deleted.
    backup = plan_path.parent / 'pre_publish'
    for rel in publish:
        dst = SYSTEM / rel
        if dst.exists():
            saved = backup / rel
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dst, saved)
    written = []
    try:
        for rel in publish:
            dst = SYSTEM / rel
            state = (dst.stat().st_mtime_ns, digest(dst.read_bytes())) if dst.exists() else None
            if state != before.get(rel):
                raise ValueError('Live mtime/content drift during publish: ' + rel)
            dst.parent.mkdir(parents=True, exist_ok=True)
            written.append(rel)
            shutil.copyfile(cs / rel, dst)
            if digest(dst.read_bytes()) != digest((cs / rel).read_bytes()):
                raise ValueError('Publish verification failed: ' + rel)
    except Exception:
        # Restore existing artifacts. New, unreferenced artifacts are retained
        # for inspection, never deleted under the D: no-delete contract.
        for rel in reversed(written):
            saved = backup / rel
            if saved.exists():
                shutil.copy2(saved, SYSTEM / rel)
        write_json(plan_path.parent / 'publish_failed.json', {'attempted_paths': written, 'restored_existing': True,
                   'new_artifacts_retained': [r for r in written if not (backup / r).exists()]})
        raise
    write_json(plan_path.parent / 'published.json', {'paths': publish, 'affected': affected, 'candidate': str(cs)})
    report(p, 'APPLIED', plan_path, f'Affected partitions: {affected}. All gates passed in isolated candidate. D2 waiver applies only to KTCP kp-t01..03.')
    print('APPLIED', affected)
    return 0


def main():
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--plan', action='store_true')
    mode.add_argument('--apply', nargs='?', const='latest')
    ap.add_argument('--review', type=Path)
    args = ap.parse_args()
    try:
        with refresh_lock():
            if args.plan:
                return plan()
            path = Path(read_json(SYSTEM / 'work/refresh/latest.json')['plan']) if args.apply == 'latest' else Path(args.apply)
            try:
                return apply(path, args.review)
            except Exception as exc:
                if path.is_file():
                    report(read_json(path), 'STOP', path, str(exc))
                raise
    except (ValueError, OSError, KeyError) as exc:
        print('STOP:', exc)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
