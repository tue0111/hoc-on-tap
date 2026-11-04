import sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(R))
from retrieval import courses as C
from scripts import v3_eval_course as E
from scripts import v3_eval_learner_notes as L
for c in C.load_registry()['courses']:
    if c['id']=='external': c['tier']='retrieval'
for c in C.load_registry()['courses']:
    if c['tier']!='retrieval' or c['id'] in C.PSEUDO: continue
    sys.argv=['eval','--course',c['id'],'--tag','_wave5']; E.main()
    r=json.loads((R/f"reports/v3/{c['id']}_eval_wave5.json").read_text(encoding='utf-8'))
    assert r['all_pass'], c['id']
sys.argv=['eval','--tag','_wave5']; L.main()
for rec in json.loads((R/'evals/v3/FROZEN.json').read_text(encoding='utf-8')).values():
    assert hashlib.sha256((R/rec['file']).read_bytes()).hexdigest()==rec['sha256']
print('All enabled course gates and frozen hashes PASS')
