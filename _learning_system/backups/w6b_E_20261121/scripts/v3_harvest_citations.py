import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from research.citations import references
R=Path(__file__).resolve().parents[1]
rows={}
for p in sorted((R/'data/normalized').glob('*.pages.jsonl')):
    layer='learner_notes' if p.name.startswith('learner-notes.') else 'curriculum'
    for line in p.read_text(encoding='utf-8').splitlines():
        pg=json.loads(line)
        for ref,variant in references(pg.get('text','')):
            r=rows.setdefault(ref,{'ref_normalized':ref,'variants':set(),'courses':set(),'occurrences':set()})
            r['variants'].add(variant); r['courses'].add(pg.get('course_id') or p.name.split('.')[0]); r['occurrences'].add((pg['source_id'],pg['page'],layer))
out=[]
for r in sorted(rows.values(),key=lambda x:x['ref_normalized']):
    out.append({**r,'variants':sorted(r['variants']),'courses':sorted(r['courses']),'occurrences':[{'source_id':s,'page':p,'layer':layer} for s,p,layer in sorted(r['occurrences'])]})
(R/'research/curriculum_citations.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('References:',len(out))
for r in out: print(r['ref_normalized'],len(r['occurrences']))
