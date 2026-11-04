"""D1 verification; candidate tiers are temporary in-memory only."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from retrieval import courses as C
from retrieval.config import SYSTEM
from scripts import v3_eval_course as E

if __name__=='__main__':
    frozen=json.loads((SYSTEM/'evals/v3/FROZEN.json').read_text(encoding='utf-8'))
    for rec in frozen.values():
        assert hashlib.sha256((SYSTEM/rec['file']).read_bytes()).hexdigest()==rec['sha256']
    targets=[c for c in C.load_registry()['courses'] if c['id'] not in C.PSEUDO and c['tier']!='core']
    for c in targets: c['tier']='retrieval'
    for c in targets:
        print('COURSE',c['id'],flush=True)
        sys.argv=['v3_eval_course','--course',c['id'],'--tag','_d1_candidate']
        E.main()
