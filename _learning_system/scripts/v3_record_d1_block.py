"""Record approved D1 trial and its stop condition, preserving frozen suites."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
import yaml
R=Path(__file__).resolve().parents[1]
def js(p): return json.loads((R/p).read_text(encoding='utf-8'))
p=R/'autopilot/v3_progress.yaml'
original=p.read_bytes()
progress=yaml.safe_load(original)
now=datetime.now(timezone.utc).isoformat()
for rec in js('evals/v3/FROZEN.json').values():
    assert hashlib.sha256((R/rec['file']).read_bytes()).hexdigest()==rec['sha256']
reports=sorted((R/'reports/v3').glob('*_eval_d1_candidate.json'))
assert len(reports)==10
lines=['# D1 trial — blocked and reverted','',
       'Authorization: learner approved D1 and D2 via "ok, làm xong qua Wave 5".',
       'D2 waiver applies only to kp-t01, kp-t02, kp-t03; raw frozen results remain unchanged.',
       'Candidate tiers were retrieval only in memory during evaluation; registry was never promoted.',
       '', '| Course | include@5 | chapter@1 | source-bound | insufficient | Raw pass |',
       '|---|---:|---:|---:|---:|---|']
for path in reports:
    r=json.loads(path.read_text(encoding='utf-8')); m=r['metrics']
    lines.append(f"| {r['course_id']} | {m['direct_must_include']:.3f} | {m['direct_chapter_at1']:.3f} | {m['source_bound']:.3f} | {m['insufficient']:.3f} | {r['all_pass']} |")
lines += ['', '## Check and decision', '',
          '- KTCP meets numeric gates with the approved D2 exception; raw topic_owner remains 0/3.',
          '- KTNH meets numeric gates under D1.',
          '- TCDN1 remains chapter@1 4/12 = 0.333 < 0.80; multi-topic summary src-0177 dominates top-1. Removing course cues alone does not resolve this.',
          '- Existing retrieval course TCHCSN regresses from 10/12 to 9/12 = 0.75 < 0.80. This triggers the explicit D1 stop condition.',
          '- Core regression under D1: IDENTICAL, reports/v3/run_20261011_214229.',
          '- D1 lexical change reverted to preserve the previously verified runtime. No tiers changed. All 11 frozen V3 eval hashes unchanged.',
          '- G4 remains blocked. Wave 5 not started; external research and refresh remain disabled.',
          '- Needed: permission for a broader source-role/ranking diagnosis and narrowly scoped repair beyond uniform D1 cue removal. Do not change hybrid weights, frozen evals, or core behavior.',
          '- D2 is approved, not pending. It does not waive any other failed gate.']
(R/'reports/v3/D1_rerun.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
progress['steps']['D1.trial']={'status':'blocked','at':now,'note':'Authorized trial regresses TCHCSN; reverted. reports/v3/D1_rerun.md'}
progress['steps']['D2.waiver']={'status':'done','at':now,'note':'Learner approved waiver of kp-t01/kp-t02/kp-t03 only; evals unchanged.'}
progress['current_step']='G4 BLOCKED: D1 trial regressed TCHCSN and was reverted; D2 approved; Wave 5 not started'
progress['escalations'].append({'step':'D1.trial','reason':'TCHCSN chapter@1 0.75<0.80 after uniform cue stripping; TCDN1 remains 0.333. Change reverted, registry unchanged.','at':now,'resolution':None})
assert p.read_bytes()==original
p.write_text(yaml.safe_dump(progress,allow_unicode=True,sort_keys=False),encoding='utf-8')
for rel in ['reports/v3/G4.md','reports/v3/V3_FINAL.md']:
    f=R/rel
    f.write_text(f.read_text(encoding='utf-8').rstrip()+'\n\n## D1/D2 update\n\nLearner approved D1 and the three-row D2 waiver. D1 trial caused a TCHCSN gate regression and did not repair TCDN1; it was reverted. No tiers changed. D2 is no longer awaiting approval. G4 still blocked; see `reports/v3/D1_rerun.md`.\n',encoding='utf-8')
print('D1 blocked, reverted; D2 approval recorded; frozen hashes unchanged')
