"""Mechanical Wave 4 documentation synchronization; no course/source edits."""
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime, timezone
import yaml

ROOT = Path(__file__).resolve().parents[1]
STAMP = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
BACKUP = ROOT / 'backups' / ('wave4_' + STAMP)
def read(rel): return (ROOT / rel).read_text(encoding='utf-8')
def js(rel): return json.loads(read(rel))
def yl(rel): return yaml.safe_load(read(rel))
def dump(obj): return yaml.safe_dump(obj, allow_unicode=True, sort_keys=False)
pending = {}
original = {}
def stage(rel, text):
    p = ROOT / rel
    original[rel] = p.read_bytes() if p.exists() else None
    pending[rel] = text
def append(rel, text): stage(rel, read(rel).rstrip() + '\n\n' + text.strip() + '\n')

registry = {c['id']: c for c in yl('curriculum/course_registry.yaml')['courses']}
progress = yl('autopilot/v3_progress.yaml')
if progress.get('steps', {}).get('4.1', {}).get('status') == 'done':
    raise SystemExit('Wave 4 docs already synchronized; use targeted patches, not a repeated bulk update.')
gate_ids = dict(zip(['ke-toan-tai-chinh-2','ke-toan-chi-phi','kiem-toan-1','ke-toan-ngan-hang','kinh-doanh-va-nghiep-vu','luat-kinh-doanh','tai-chinh-doanh-nghiep-1','ngan-hang-thuong-mai','thi-truong-tai-chinh','tai-chinh-hanh-chinh-su-nghiep','learner-notes'], ['G1','G2a','G2b','G2c','G3a','G3b','G3c','G3d','G3e','G3f','G3g']))
for rec in js('evals/v3/FROZEN.json').values():
    assert hashlib.sha256((ROOT/rec['file']).read_bytes()).hexdigest() == rec['sha256']
old_freeze = js('pilot/core_freeze_manifest.json')
for rel, rec in old_freeze['frozen_suites'].items():
    assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest() == rec['sha256'], rel

# Preserve metadata for legacy entries; parse headers for newly discovered extracts.
existing = {r['extract_path']: r for r in js('extracts/index.json')}
rows = []
for p in sorted((ROOT/'extracts').rglob('*.md')):
    if p.name == 'README.md': continue
    rel = p.relative_to(ROOT).as_posix()
    if rel in existing: rows.append(existing[rel]); continue
    text = p.read_text(encoding='utf-8')
    sid = re.search(r'src-\d+', p.name)
    row = {'source_id': sid.group() if sid else None, 'extract_path': rel}
    for key in ['page_count','pages_extracted','char_count']:
        m = re.search(r'^'+key+r':\s*(\d+)', text, re.M)
        row[key] = int(m[1]) if m else None
    row.update(ok='## TEXT' in text, metadata_origin='extract_header')
    rows.append(row)
stage('extracts/index.json', json.dumps(rows, ensure_ascii=False, indent=2)+'\n')
stage('extracts/README.md', 'Legacy capped extracts (≤12 pages). Canonical text is `data/normalized/`.\n')

stats=[]
for cid, gate in gate_ids.items():
    cov=js(f'data/normalized/{cid}.coverage.json')
    docs=[json.loads(x) for x in read(f'data/normalized/{cid}.documents.jsonl').splitlines() if x.strip()]
    meta=js(f'data/indexes/3.0.0/{cid}/meta.json')
    concepts=yl(f'curriculum/concepts/{cid}.yaml')['concepts'] if cid!='learner-notes' else []
    evalpath=f'reports/v3/{cid}_eval_g3x_fixed.json'
    if not (ROOT/evalpath).exists(): evalpath=f'reports/v3/{cid}_eval_run3.json'
    ev=js(evalpath)
    stats.append({'id':cid,'tier':registry[cid]['tier'],'sources':len(docs),'pages':cov['page_count'],'chars':cov['total_chars'],'chunks':meta['chunk_count'],'concepts':len(concepts),'metrics':ev['metrics'],'eval_report':evalpath,'gate':gate,'gate_status':progress['gates'][gate]['status'],'thin':cov.get('thin_documents',[])})
    if cid=='learner-notes': continue
    rel=f'curriculum/course_manifests/{cid}.yaml'
    text=read(rel)
    # Observed lecture scripts, excluding slides/exams and chapter zero introductions.
    chapters=sorted({d['chapter'] for d in docs if d.get('chapter') and (d.get('unit_script') or d.get('source_type')=='lecture_note')})
    for key,value in [('chapters_with_script_files',chapters),('advertised_chapters_missing_files',[])]:
        pattern=r'^  '+key+r':[^\n]*(?:\n  -[^\n]*)*'
        replacement='  '+key+': '+json.dumps(value)
        if re.search(pattern,text,re.M): text=re.sub(pattern,replacement,text,flags=re.M)
        else: text=text.replace('coverage:\n','coverage:\n'+replacement+'\n',1)
    if cid=='ke-toan-tai-chinh-2':
        text=text.replace('slides, script_chapters_3_and_4,','slides,')
        for n in [3,4]:
            text=text.replace(f'files_in_folder: false\n      note: Advertised in Chương 0. No Chương {n}.pdf in folder.',f'files_in_folder: true\n      note: V3 observed full Chapter {n} document and unit scripts; see normalized corpus.')
    v3={'tier':registry[cid]['tier'],'index':'3.0.0','gate':gate,'gate_status':progress['gates'][gate]['status'],'chunk_count':meta['chunk_count'],'coverage_evidence':f'data/normalized/{cid}.documents.jsonl','legacy_fields_note':'Pre-V3 scan fields remain historical unless explicitly updated above. V3 concepts and normalized corpus are canonical.'}
    stage(rel,text.rstrip()+'\n\n'+dump({'v3':v3}))

rel='curriculum/curriculum_manifest.yaml'
text=read(rel)
text=text.replace('quote_from_other_course: "môn cơ sở ngành" then KTTC1', 'quote_from_other_course: \'"môn cơ sở ngành" then KTTC1\'')
before=yaml.safe_load(text)
for cid,c in registry.items():
    needle='  - course_id: '+cid+'\n'
    text=re.sub('^'+re.escape(needle),lambda m: needle+'    v3_tier: '+c['tier']+'\n',text,flags=re.M)
after=yaml.safe_load(text)
for c in after['courses']: c.pop('v3_tier',None)
assert after==before
stage(rel,text)

table='| Course | Tier | Sources | Pages/slides | Characters | Chunks | Concepts | Gate |\n|---|---|---:|---:|---:|---:|---:|---|\n'
for s in stats: table+=f"| {s['id']} | {s['tier']} | {s['sources']} | {s['pages']} | {s['chars']} | {s['chunks']} | {s['concepts']} | {s['gate']} {s['gate_status']} |\n"
quality=read('reports/data_quality_report.md').replace('- Missing advertised chapters (','- [SUPERSEDED by Phase 2.1/V3; historical] Missing advertised chapters (')
stage('reports/data_quality_report.md',quality.rstrip()+'\n\n## V3\n\n'+table+'\nCounts include combined duplicates extracted for coverage; indexed chunks exclude them. Page counts include synthetic DOCX pages and PPTX slides. Extraction reports have no errors. Catalog means not enabled for runtime, even where a candidate index exists. Old capped-extract limitations are historical; image-only PPTX src-0165 still has zero extracted text.\n')
state=yl('autopilot/state.yaml')
pilot=state['pilot'].copy()
state['core_version']='9.0.0'
state['retrieval_scope']=[cid for cid,c in registry.items() if c['tier']=='retrieval' and cid not in ['learner-notes','external']]
state['expansion'].update(enabled=True,mode='curriculum_ingestion_only',authorized_by='learner',authorized_at='2026-10-11')
state['external_research'].update(enabled=False,mode='official_sources_only')
state['refresh']={'enabled':False}
assert state['pilot']==pilot and state['active_scope']==['ACCO1325','ACCO2310']
stage('autopilot/state.yaml',dump(state))
plan=read('V3_EXPANSION_PLAN.md')
tier_table=plan.split('### 4.1 Course tiers\n\n')[1].split('\n### 4.2')[0].strip()
note='Current runtime clarification: catalog also includes candidate indexes that failed a gate; these are not served. Seven curriculum courses are retrieval-enabled; KTCP, KTNH and TCDN1 remain catalog. learner-notes is non-curriculum. External updates and refresh remain disabled until G5/G6. Full-loop diagnostic/admission/state instructions apply to CORE only.'
for rel in ['README.md','AGENTS.md']:
    append(rel,'## V3 course tiers\n\n'+tier_table+'\n\n'+note+'\n\nFrom `D:\\Hoc\\_learning_system`:\n```powershell\npython -m retrieval.cli retrieve "QUESTION" --course <id>\n```\n\nSee `curriculum/course_registry.yaml` and `reports/v3/V3_FINAL.md` for current readiness. Pilot real-traffic requirements still apply to full-loop expansion, not authorized curriculum ingestion.')
contract=plan.split('## 8. RUNTIME CONTRACT TEXT')[1].split('```markdown\n')[1].split('\n```')[0]
rel='GROK_BOT_MASTER_INSTRUCTIONS.md'
text=read(rel).replace('**Validated production scope:** NLKT (ACCO1325) + KTTC1 (ACCO2310)','**Core scope (full loop):** NLKT (ACCO1325) + KTTC1 (ACCO2310) · **Retrieval scope:** see curriculum/course_registry.yaml (tier: retrieval)')
text=text.replace('## 4. STARTUP WORKFLOW',contract+'\n\n'+note+'\n\n## 4. STARTUP WORKFLOW',1)
stage(rel,text)
rel='.grok/agents/learning-director.md'
stage(rel,read(rel).replace('## Output shape',contract+'\n\n'+note+'\n\n## Output shape',1))
bullets=[line for line in contract.splitlines() if line.startswith('- ')][:4]
for rel in ['skills/curriculum-retrieval/SKILL.md','.grok/skills/curriculum-retrieval/SKILL.md']:
    append(rel,'## 3A. COURSE TIERS (v3)\n\n'+ '\n'.join(bullets)+'\n\n'+note+'\n\nFor retrieval-tier courses, use the CLI with explicit course before the legacy manifest fallback. Learner notes are always labeled "tài liệu cá nhân của bạn, không phải giáo trình"; never curriculum evidence.')

report='# V3 readiness — Wave 4\n\nG4 is BLOCKED under the literal all-course-gates-pass requirement: G2a, G2c and G3c still fail. Documentation can be synchronized without promoting these courses. Wave 5 is not started.\n\n'+table+'\n## Evaluation metrics\n\n'
for s in stats: report+=f"- {s['id']}: `{json.dumps(s['metrics'],ensure_ascii=False)}`; `{s['eval_report']}`.\n"
report+='\nAggregate gate pass is not a claim that every individual row passes. Core remains NLKT + KTTC1, index 2.0.0, 810 chunks. Real Grok bot acceptance by the learner has not been performed.\n\n## Open items\n\n- D1: explicit approval required before removing course cues from lexical scoring (KTCP/KTNH/TCDN1 ranking).\n- D2: KTCP frozen topic-owner expectations conflict with specification; require learner waiver or a new designer-authored supplemental suite. Existing evals must not be edited.\n- KTTC2 course code, NHTM law vintage, TCDN1 exam duration conflicts remain unresolved.\n- Wave 5 external verification and Wave 6 refresh remain disabled.\n- Core freeze and regression verification results are in G4.md.\n\n## Learner-material list — confirmation pending\n\n'
for line in read('data/normalized/learner-notes.documents.jsonl').splitlines():
    d=json.loads(line); report+=f"- {d['source_id']}: {d['relative_path']} ({d['page_count']} pages/slides, {d['char_count']} characters).\n"
report+='\nImage-only src-0165: 14 slides, zero extracted characters, no indexed text. No OCR or visual-content validation claimed. All learner material stays separate from curriculum.\n'
stage('reports/v3/V3_FINAL.md',report)
stage('reports/v3/wave4_stats.json',json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
for i in range(1,8): progress['steps'][f'4.{i}']={'status':'done','at':STAMP,'note':'Synchronized from verified registry/artifacts; catalog failures preserved.'}
progress.update(current_wave=4,current_step='4.8 freeze and core regression verification')
stage('autopilot/v3_progress.yaml',dump(progress))

# Guard against changes between reading and committing; preserve every overwritten file.
for rel,data in original.items():
    p=ROOT/rel
    assert (p.read_bytes() if p.exists() else None)==data, rel
BACKUP.mkdir(parents=True)
for rel,text in pending.items():
    if original[rel] is not None:
        b=BACKUP/rel; b.parent.mkdir(parents=True,exist_ok=True); b.write_bytes(original[rel])
    p=ROOT/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text,encoding='utf-8')
(BACKUP/'core_freeze_manifest.json').write_bytes((ROOT/'pilot/core_freeze_manifest.json').read_bytes())
print(json.dumps({'updated':len(pending),'extracts':len(rows),'backup':str(BACKUP)},ensure_ascii=False))
