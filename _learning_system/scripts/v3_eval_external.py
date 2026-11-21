"""Five frozen G5 contracts plus additive-isolation checks; no production enable."""
import sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(R))
sys.path.insert(0,str(R/'work/v3_deps'))
import jsonschema
from retrieval import courses as C
from retrieval.retrieve import retrieve,_retrieve_legacy
from retrieval.director import answer
from retrieval.external import LABEL,notes,records
from research.citations import slug
import yaml
for c in C.load_registry()['courses']:
    if c['id']=='external': c['tier']='retrieval'
path=R/'evals/v3/external_retrieval.jsonl'
frozen=R/'evals/v3/FROZEN.json'; f=json.loads(frozen.read_text(encoding='utf-8'))
sha=hashlib.sha256(path.read_bytes()).hexdigest()
if 'external' in f: assert f['external']['sha256']==sha
else:
    f['external']={'file':path.relative_to(R).as_posix(),'sha256':sha,'first_run_pending':True}
    frozen.write_text(json.dumps(f,ensure_ascii=False,indent=2),encoding='utf-8')
results=[]
for line in path.read_text(encoding='utf-8').splitlines():
    row=json.loads(line); pkg=retrieve(row['question'],row['filters'])
    jsonschema.validate(pkg,json.loads((R/'schemas/evidence_package.schema.json').read_text(encoding='utf-8')))
    updates=pkg.get('regulation_updates') or pkg.get('v3',{}).get('regulation_updates') or []
    if row['check']=='curriculum_update': ok=pkg['layer']=='curriculum' and any(u['ref']==row['expected_ref'] for u in updates)
    elif row['check']=='no_update': ok=pkg['layer']=='curriculum' and not updates
    elif row['check']=='external': ok=pkg['layer']=='external' and bool(pkg['items']) and any(row['expected_ref'] in i['text'] for i in pkg['items'])
    else: ok=pkg['layer']=='external' and pkg['coverage']=='insufficient' and not pkg['items']
    if pkg['layer']=='external': ok=ok and LABEL in answer(row['question'],row['filters'])['answer']
    else:
        legacy=_retrieve_legacy(row['question'],row['filters'])
        assert pkg['items']==legacy['items'] and pkg['coverage']==legacy['coverage'] and pkg['unknowns']==legacy['unknowns']
    results.append({'id':row['id'],'pass':bool(ok),'layer':pkg['layer'],'coverage':pkg['coverage'],'updates':[r['ref'] for r in updates],'source_ids':[i['source_id'] for i in pkg['items']]})
citations=json.loads((R/'research/curriculum_citations.json').read_text(encoding='utf-8'))
for cit in citations: assert (R/'research/regulations'/(slug(cit['ref_normalized'])+'.yaml')).exists()
schema=yaml.safe_load((R/'research/research_evidence.schema.yaml').read_text(encoding='utf-8'))['regulation_record']
violations=[]
for rec in records().values():
    assert all(k in rec for k in schema['required'] if k!='evidence_status')
    if rec['status'] not in schema['status_enum']: violations.append(f"{rec['ref']}: status={rec['status']!r} not in enum")
    assert rec['layer']=='external' and len(rec['key_changes'])<=8
    # W6b G24: enum-validate evidence_status for every record; no implicit OBSERVED. Violations fail all_pass (not just assert).
    ev=rec.get('evidence_status')
    if ev not in ('OBSERVED','INFERRED','UNKNOWN'): violations.append(f"{rec['ref']}: evidence_status={ev!r} not in enum")
    if rec['status']=='unknown': assert rec['unknown_reason']
    else:
        if ev not in ('OBSERVED','INFERRED'): violations.append(f"{rec['ref']}: status={rec['status']} requires evidence_status OBSERVED/INFERRED, got {ev!r}")
        elif ev=='OBSERVED' and not any(x.get('authority')=='official' for x in rec['sources']): violations.append(f"{rec['ref']}: OBSERVED requires >=1 official source")
    for k in rec['key_changes']: assert all(f in k for f in schema['key_change_required'])
res={'results':results,'all_pass':all(x['pass'] for x in results) and not violations,'sha256':sha,'records':len(records()),'record_contracts':'FAIL' if violations else 'PASS','record_violations':violations,'additive_isolation':'PASS'}
if f['external'].get('first_run_pending'):
    f['external'].pop('first_run_pending'); f['external']['first_run_results']=results
    frozen.write_text(json.dumps(f,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'reports/v3/external_eval.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(res,ensure_ascii=False,indent=2))
sys.exit(0 if res['all_pass'] else 1)
