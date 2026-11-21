"""Isolated layer-C retrieval and additive regulation status notes."""
from functools import lru_cache
import json,re
import numpy as np
import yaml
from retrieval.config import SYSTEM
from research.citations import references
from retrieval.textutil import tokenize,fold

LABEL='theo quy định hiện hành (nguồn ngoài giáo trình)'
CUES=re.compile(r'hiện hành|mới nhất|cập nhật|còn hiệu lực|thay thế|\bifrs\b|quy định mới',re.I)
def active():
    from retrieval.courses import tier
    return tier('external')=='retrieval'
@lru_cache(maxsize=1)
def records():
    result={}
    for path in sorted((SYSTEM/'research/regulations').glob('*.yaml')):
        rec=yaml.safe_load(path.read_text(encoding='utf-8'))
        rec['record']=path.relative_to(SYSTEM).as_posix()
        result[rec['ref']]=rec
    return result
def notes(pkg):
    if not active() or pkg.get('layer')!='curriculum' or not pkg.get('items'): return []
    from retrieval.partition import get_partition_index
    from retrieval.retrieve import get_index
    idx=get_partition_index(pkg['partition']) if pkg.get('partition') else get_index()
    byid={c['chunk_id']:c['text'] for c in idx.chunks}
    found=set()
    for item in pkg.get('items',[]):
        found.update(ref for ref,_ in references(byid.get(item.get('chunk_id'),item.get('text',''))))
    out=[]
    for ref in sorted(found):
        rec=records().get(ref)
        if not rec or rec['status'] not in {'replaced','amended','expired'}: continue
        out.append({k:rec.get(k) for k in ['ref','status','replaced_by','amended_by','effective_from','scope','record','sources','checked_at']})
    return out
def retrieve_external(question,ext,filters=None,top_k=None):
    from retrieval.partition import _empty_package,get_partition_index
    from retrieval.retrieve import _to_item
    analysis={'mode':'external','intent':'source_lookup','detected_concepts':[],'course_scope':'external','chapter':None}
    pkg=_empty_package(question,'external',ext['tier'],analysis,[])
    pkg.update(layer='external',v3={'label':LABEL,'checked_at':'2026-10-11'})
    if not active():
        pkg['unknowns']=['external_not_enabled']; return pkg
    idx=get_partition_index('external')
    qrefs={r for r,_ in references(question)}
    # Short instrument notation is useful only when it uniquely identifies a
    # checked record; never infer a bare law name's year or version.
    if not qrefs and re.search(r'\btt\s*200\b',fold(question)):
        qrefs={'Thông tư 200/2014/TT-BTC'}
    if qrefs:
        unresolved=[r for r in qrefs if r not in records() or records()[r]['status']=='unknown']
        if unresolved:
            pkg['unknowns']=['regulation_status_unverified:'+r for r in unresolved]; return pkg
    if 'ifrs' in fold(question):
        pkg['unknowns']=['ifrs_current_framework_unverified']; return pkg
    tokens=tokenize(CUES.sub(' ',question))
    scores=idx.bm25(tokens)
    selected=[]
    for i in np.argsort(-scores):
        c=idx.chunks[i]
        if scores[i]<=0: continue
        if qrefs and not any(ref in c['text'] for ref in qrefs): continue
        item=_to_item(c,float(scores[i]),analysis)
        item.update(source=c['url'],evidence_status=c.get('evidence_status','OBSERVED'))
        selected.append(item)
        if len(selected)>=(top_k or 5): break
    pkg.update(items=selected,evidence=selected,coverage='partial' if selected else 'insufficient')
    pkg['unknowns']=['status_snapshot_not_exhaustive_current_legal_advice'] if selected else ['no_verified_external_evidence']
    return pkg
def note_lines(pkg):
    rows=pkg.get('regulation_updates') or pkg.get('v3',{}).get('regulation_updates') or []
    out=[]
    for rec in rows:
        target=rec['replaced_by'] or ', '.join(rec.get('amended_by') or []) or rec['status']
        url=(rec.get('sources') or [{}])[0].get('url','')
        out.append(f"Theo quy định hiện hành: {rec['ref']} — {rec['status']}: {target} (hiệu lực thay đổi {rec['effective_from'] or 'chưa xác minh'}, nguồn {url}). {rec['scope']} [Kiểm tra {rec['checked_at']}; không đổi đáp án theo giáo trình.]" )
    return out
