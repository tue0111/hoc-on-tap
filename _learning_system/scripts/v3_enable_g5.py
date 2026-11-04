import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import yaml
R=Path(__file__).resolve().parents[1]
def read(p): return (R/p).read_text(encoding='utf-8')
def yl(p): return yaml.safe_load(read(p))
def js(p): return json.loads(read(p))
assert js('reports/v3/external_eval.json')['all_pass']
run=sorted((R/'reports/v3').glob('run_*'))[-1]
assert (run/'diff.txt').read_text(encoding='utf-8')=='IDENTICAL'
assert len(list(run.glob('*.stdout.txt')))==8
assert all('Traceback (most recent call last)' not in p.read_text(encoding='utf-8') for p in run.glob('*.stdout.txt'))
for rec in js('evals/v3/FROZEN.json').values():
    assert hashlib.sha256((R/rec['file']).read_bytes()).hexdigest()==rec['sha256']
registry=yl('curriculum/course_registry.yaml')
for c in registry['courses']:
    if c['tier']=='retrieval': assert js(f"reports/v3/{c['id']}_eval_wave5.json")['all_pass']
for c in registry['courses']:
    if c['id']=='external': c['tier']='retrieval'
assert [c['id'] for c in registry['courses'] if c['tier']=='catalog']==['ke-toan-chi-phi','ke-toan-ngan-hang','tai-chinh-doanh-nghiep-1']
stamp=datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
b=R/'backups'/('pre_g5_enable_'+stamp); b.mkdir(parents=True)
for rel in ['curriculum/course_registry.yaml','autopilot/state.yaml','autopilot/v3_progress.yaml']:
    dst=b/rel; dst.parent.mkdir(parents=True,exist_ok=True); dst.write_bytes((R/rel).read_bytes())
(R/'curriculum/course_registry.yaml').write_text(yaml.safe_dump(registry,allow_unicode=True,sort_keys=False),encoding='utf-8')
state=yl('autopilot/state.yaml'); state['external_research'].update(enabled=True,mode='official_sources_only',verified_status_records=7,unknown_status_records=62,checked_at='2026-10-11')
assert state['refresh']['enabled'] is False
(R/'autopilot/state.yaml').write_text(yaml.safe_dump(state,allow_unicode=True,sort_keys=False),encoding='utf-8')
progress=yl('autopilot/v3_progress.yaml')
for i,note in [('5.1','67 raw citation forms; all normalized page files scanned, learner occurrences labeled separately.'),('5.2','69 records: 7 verified, 62 unknown with reasons; official search logs; 23 external chunks; one 7-page PDF extracted, 10 TT99 PDF downloads unavailable due certificate chain.'),('5.3','Additive notes; explicit course/core/learner routing priority preserved; no curriculum item/coverage changes; external answers labeled.')]:
    progress['steps'][i]={'status':'done','at':stamp,'note':note}
progress['gates']['G5']={'status':'pass','report':'reports/v3/G5.md','eval':'5/5','core_regression':'IDENTICAL','candidate_regression':run.relative_to(R).as_posix(),'limitations':'62 unknown status records; official PDF download gaps; no human bot acceptance.'}
progress.update(current_wave=5,current_step='G5 PASS; verifying enabled runtime, then PAUSE. Next R1 under A2.3, before Wave 6.')
(R/'autopilot/v3_progress.yaml').write_text(yaml.safe_dump(progress,allow_unicode=True,sort_keys=False),encoding='utf-8')
for rel in ['README.md','AGENTS.md','GROK_BOT_MASTER_INSTRUCTIONS.md','.grok/agents/learning-director.md','skills/curriculum-retrieval/SKILL.md','.grok/skills/curriculum-retrieval/SKILL.md']:
    p=R/rel; text=p.read_text(encoding='utf-8')
    text=text.replace('External updates and refresh remain disabled until G5/G6.','External updates are enabled after G5 (7 checked status records, 62 unknown); refresh remains disabled until G6.')
    p.write_text(text,encoding='utf-8')
note='''
## Wave 5 external status plane

G5 PASS: 5/5 frozen external tests; candidate core regression IDENTICAL. Final enabled-runtime verification is recorded in G5.md.
67 harvested citation forms (including incomplete regex candidates) map to 69 records including two required research leads: 7 checked statuses, 62 unknown. Unknown is not a legal conclusion and is not indexed as positive evidence.
23 isolated external chunks: checked status summaries plus one official 7-page PDF (14,659 extracted characters). Ten TT99 PDF segments could not be downloaded because the CDN certificate chain failed verification; security checks were not disabled. TT99 replacement scope is supported by official Ministry/Official Gazette pages, not a claim to have indexed its full text.
All search attempts are in research/search_logs; records in research/regulations; downloads and hashes in research/source_downloads.json.
Routing keeps explicit course filters, learner notes and named core curriculum scope ahead of external keyword detection to preserve frozen core questions (including IFRS asked within NLKT). Use --course external to request an external-only answer. Notes are appended only for instruments actually cited by retrieved curriculum chunks.
R1 is pending after the G5 pause; KTCP, KTNH and TCDN1 remain catalog. No Wave 6/7 work. Grok bot live acceptance remains unverified.
'''
for rel in ['README.md','reports/v3/V3_FINAL.md','reports/data_quality_report.md']:
    p=R/rel; p.write_text(p.read_text(encoding='utf-8').rstrip()+'\n\n'+note.strip()+'\n',encoding='utf-8')
(R/'reports/v3/G5.md').write_text('# G5 — PASS\n\n'+note+f'\nCandidate regression: `{run.relative_to(R).as_posix()}`.\n\nEvidence: `external_eval.json`, `external_build.json`, `*_eval_wave5.json`. Seven curriculum gates and learner-notes pass; all 12 frozen V3 hashes unchanged. No existing eval altered. Schema validation passes for all five test packages.\n',encoding='utf-8')
print('G5 enabled; final on-disk regression pending')
