import hashlib,json
from pathlib import Path
import yaml
R=Path(__file__).resolve().parents[1]
plan=(R/'V3_EXPANSION_PLAN.md').read_text(encoding='utf-8')
a2=(R/'V3_AMENDMENT_A2.md').read_text(encoding='utf-8')
assert plan.endswith(a2) or plan.rstrip().endswith(a2.rstrip())
assert plan.count('# AMENDMENT A2 (design model')==1
for r in json.loads((R/'evals/v3/FROZEN.json').read_text(encoding='utf-8')).values():
    assert hashlib.sha256((R/r['file']).read_bytes()).hexdigest()==r['sha256']
p=R/'autopilot/v3_progress.yaml'; s=yaml.safe_load(p.read_text(encoding='utf-8'))
s['gates']['G4'].update(status='pass_a2',reason='Every course has a final state; catalog failures are open items R1.',resolution='Amendment A2.1')
for e in s['escalations']:
    if e['step']=='G4': e['resolution']='Amendment A2.1'
s.update(current_wave=5,current_step='5.1 harvest curriculum citations; R1 deferred until after G5 PASS')
s['steps']['A2']={'status':'done','note':'Appended verbatim; G4 pass_a2; no tier changes; D2 waiver recorded.'}
p.write_text(yaml.safe_dump(s,allow_unicode=True,sort_keys=False),encoding='utf-8')
for rel in ['reports/v3/G4.md','reports/v3/V3_FINAL.md']:
    p=R/rel
    p.write_text(p.read_text(encoding='utf-8').rstrip()+'\n\nG4 PASS under Amendment A2.1; KTCP, KTNH, TCDN1 remain catalog (open items R1). Earlier G4 BLOCKED statements are historical and superseded. Wave 5 proceeds before R1.\n',encoding='utf-8')
print('A2 appended verbatim, G4 pass_a2, tiers unchanged')
