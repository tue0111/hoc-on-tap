"""Verify Wave 4 artifacts and record the literal G4 blocker."""
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime, timezone
import yaml
R=Path(__file__).resolve().parents[1]
def read(p): return (R/p).read_text(encoding='utf-8')
def js(p): return json.loads(read(p))
def yl(p): return yaml.safe_load(read(p))
registry={c['id']:c for c in yl('curriculum/course_registry.yaml')['courses']}
stats=js('reports/v3/wave4_stats.json')
backups=sorted((R/'backups').glob('wave4_*'))
backup=backups[-1]
freeze=js('pilot/core_freeze_manifest.json')
old=json.loads((backup/'core_freeze_manifest.json').read_text(encoding='utf-8'))
assert freeze['source_integrity']['status']=='OK' and freeze['source_integrity']['checked']==40
assert freeze['frozen_suites']==old['frozen_suites']
for rec in js('evals/v3/FROZEN.json').values():
    assert hashlib.sha256((R/rec['file']).read_bytes()).hexdigest()==rec['sha256']
for p in (R/'curriculum/course_manifests').glob('*.yaml'): yaml.safe_load(p.read_text(encoding='utf-8'))
for s in stats:
    assert freeze['v3_partitions'][s['id']]['chunk_count']==s['chunks']
    if s['id']!='learner-notes':
        m=yl(f"curriculum/course_manifests/{s['id']}.yaml")
        assert m['v3']['tier']==registry[s['id']]['tier']
        assert m['coverage']['advertised_chapters_missing_files']==[]
    if s['tier']=='retrieval': assert js(s['eval_report'])['all_pass']
curr=yl('curriculum/curriculum_manifest.yaml')
for c in curr['courses']: assert c.pop('v3_tier')==registry[c['course_id']]['tier']
prior=(backup/'curriculum/curriculum_manifest.yaml').read_text(encoding='utf-8')
prior=prior.replace('quote_from_other_course: "môn cơ sở ngành" then KTTC1','quote_from_other_course: \'"môn cơ sở ngành" then KTTC1\'')
assert curr==yaml.safe_load(prior)
state=yl('autopilot/state.yaml')
assert state['pilot']==yaml.safe_load((backup/'autopilot/state.yaml').read_text(encoding='utf-8'))['pilot']
assert not state['external_research']['enabled'] and not state['refresh']['enabled']
plan=read('V3_EXPANSION_PLAN.md')
contract=plan.split('## 8. RUNTIME CONTRACT TEXT')[1].split('```markdown\n')[1].split('\n```')[0]
for p in ['GROK_BOT_MASTER_INSTRUCTIONS.md','.grok/agents/learning-director.md']: assert contract in read(p)
bullets=[line for line in contract.splitlines() if line.startswith('- ')][:4]
for p in ['skills/curriculum-retrieval/SKILL.md','.grok/skills/curriculum-retrieval/SKILL.md']:
    assert all(b in read(p) for b in bullets)
extracts={p.relative_to(R).as_posix() for p in (R/'extracts').rglob('*.md') if p.name!='README.md'}
assert extracts=={r['extract_path'] for r in js('extracts/index.json')}
run=sorted((R/'reports/v3').glob('run_*'))[-1]
assert (run/'diff.txt').read_text(encoding='utf-8')=='IDENTICAL'
logs=list(run.glob('*.stdout.txt'))
assert len(logs)==8 and not any('Traceback (most recent call last)' in p.read_text(encoding='utf-8') for p in logs)
blocked=[s['id'] for s in stats if s['gate_status']!='pass']
assert len(blocked)==3
report=f'''# G4 — documentation verified; gate blocked

- Core regression: IDENTICAL, `{run.relative_to(R).as_posix()}` (8 suite logs; no traceback).
- Core source integrity: OK, 40/40. Frozen core suite hashes identical to pre-Wave-4 manifest.
- All 11 frozen V3 eval hashes unchanged. Seven enabled curriculum course reports and learner-notes report pass.
- 212 extract entries match the on-disk legacy extracts (README excluded).
- 12 course manifests parse; 10 ingested course manifests have observed chapter coverage and actual tiers.
- Curriculum manifest: only v3_tier added, plus correction of a pre-existing invalid quoted scalar; text meaning preserved.
- Runtime contract matches plan section 8 verbatim in both full instructions; first four bullets match in both skills.
- Pilot fields unchanged; external research and refresh disabled. 11 candidate partitions recorded in freeze metadata.
- Backups: `{backup.relative_to(R).as_posix()}`. No Git repository; no commit or git initialization.

## Gate decision

G4 BLOCKED: the plan requires all course gates to pass. Still failing: {', '.join(blocked)}. No waiver inferred and no tier promoted. Wave 5 not started.

D1 needs explicit approval to remove course-name cues from partition lexical queries, followed by frozen-suite reruns. D2 needs a learner waiver for the three incorrectly specified KTCP topic-owner rows, or a designer-authored supplemental eval (existing evals remain frozen). Human Grok bot runtime acceptance remains unverified.
'''
(R/'reports/v3/G4.md').write_text(report,encoding='utf-8')
p=yl('autopilot/v3_progress.yaml')
now=datetime.now(timezone.utc).isoformat()
for step in ['4.8','4.9']:
    p['steps'][step]={'status':'done','at':now,'note':'Verified; reports/v3/G4.md and V3_FINAL.md'}
p['gates']['G4']={'status':'blocked','report':'reports/v3/G4.md','core_regression':'IDENTICAL','reason':'All-course gate requirement unmet: G2a, G2c, G3c.'}
p.update(current_wave=4,current_step='G4 BLOCKED: awaiting D1/D2 resolution; Wave 5 not started')
p['escalations'].append({'step':'G4','reason':'Three course gates remain failed. Explicit D1 approval and D2 resolution needed; no gate waiver assumed.','at':now,'resolution':None})
(R/'autopilot/v3_progress.yaml').write_text(yaml.safe_dump(p,allow_unicode=True,sort_keys=False),encoding='utf-8')
print(json.dumps({'docs':'PASS','regression':str(run),'G4':'BLOCKED','courses':blocked},ensure_ascii=False))
