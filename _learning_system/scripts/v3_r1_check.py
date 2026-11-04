"""R1 non-target rank/score invariant and candidate gates; never edits frozen evals."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from retrieval import courses as C
from retrieval.config import SYSTEM
from retrieval.retrieve import retrieve
from scripts.v3_eval_course import run_row, main as eval_main

TARGETS = ('ke-toan-chi-phi', 'ke-toan-ngan-hang', 'tai-chinh-doanh-nghiep-1')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--phase', required=True)
    ap.add_argument('--candidates', action='store_true')
    args = ap.parse_args()
    rep = SYSTEM / 'reports/v3'
    snapshot = {}
    changed = []
    for c in C.load_registry()['courses']:
        cid = c['id']
        if c['tier'] != 'retrieval' or cid in C.PSEUDO or cid in TARGETS:
            continue
        rows = [json.loads(l) for l in (SYSTEM / f'evals/v3/{cid}_retrieval.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
        results, ranked = [], []
        for row in rows:
            results.append(run_row(row))
            filters = {'mode': row['mode']} if row.get('mode') else {}
            if row.get('pass_course'):
                filters['course_id'] = row['course']
            pkg = retrieve(row['question'], filters=filters)
            ranked.append({'id': row['id'], 'items': [{k: it.get(k) for k in ('chunk_id', 'source_id', 'chapter', 'relevance_score')} for it in pkg.get('items', [])]})
        baseline = json.loads((rep / f'{cid}_eval_g3x_fixed.json').read_text(encoding='utf-8'))['results']
        if results != baseline:
            changed.append(cid)
        snapshot[cid] = {'results': results, 'ranked': ranked}
    encoded = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, indent=2).encode('utf-8')
    (rep / f'r1_{args.phase}_non_targets.json').write_bytes(encoded)
    if changed:
        raise SystemExit(f'STOP: results differ from G3x: {changed}')
    if args.phase != 'before':
        if encoded != (rep / 'r1_before_non_targets.json').read_bytes():
            raise SystemExit('STOP: non-target rank/score bytes changed')
    print('NON_TARGETS_IDENTICAL', len(snapshot), hashlib.sha256(encoded).hexdigest())
    if args.candidates:
        for cid in TARGETS:
            C.get_course(cid)['tier'] = 'retrieval'
        for cid in TARGETS:
            sys.argv = ['v3_eval_course.py', '--course', cid, '--tag', f'_r1_{args.phase}']
            eval_main()
        cid = TARGETS[0]
        raw = json.loads((rep / f'{cid}_eval_r1_{args.phase}.json').read_text(encoding='utf-8'))
        waived = {'kp-t01', 'kp-t02', 'kp-t03'}
        kept = [r for r in raw['results'] if r['id'] not in waived]
        assert {r['id'] for r in raw['results'] if r['id'] in waived} == waived
        gates = dict(raw['gates'])
        topic = [r for r in kept if r['category'] == 'topic_owner']
        gates['topic_owner'] = not topic or all(r['pass'] for r in topic)
        adjusted = {'label': 'D2 waiver', 'excluded_ids': sorted(waived), 'raw_report': f'{cid}_eval_r1_{args.phase}.json', 'gates': gates, 'all_pass': all(gates.values())}
        (rep / f'ktcp_r1_{args.phase}_d2.json').write_text(json.dumps(adjusted, indent=2), encoding='utf-8')
        print('D2 waiver', adjusted)


if __name__ == '__main__':
    main()
