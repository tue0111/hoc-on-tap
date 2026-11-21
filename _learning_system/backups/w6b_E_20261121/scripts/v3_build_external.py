"""Build isolated external evidence and records. Never edits curriculum data."""
import json,sys,hashlib,re
from pathlib import Path
from urllib.parse import urlparse
import yaml
R=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(R))
from research.citations import slug
from retrieval.chunking import pages_to_units
from retrieval.index import build_index
citations=json.loads((R/'research/curriculum_citations.json').read_text(encoding='utf-8'))
verified=yaml.safe_load((R/'research/verified_updates.yaml').read_text(encoding='utf-8'))['records']
known={r['ref']:r for r in verified}
logs={}
for p in (R/'research/search_logs').glob('ref_*.json'):
    x=json.loads(p.read_text(encoding='utf-8')); logs[x['ref']]=p.relative_to(R).as_posix()
out=R/'research/regulations'; out.mkdir(exist_ok=True)
refs={r['ref_normalized']:r for r in citations}
for ref in known: refs.setdefault(ref,{'courses':[],'occurrences':[],'variants':[ref]})
# W6b G04: rebuilding from the reviewed records is the DEFAULT. Regenerating records from the Wave 5 snapshot
# (verified_updates.yaml) overwrites reviewed W6b records, so it now needs the explicit --bootstrap-wave5 flag.
FROM_RECORDS = '--bootstrap-wave5' not in sys.argv
records=[]
for ref,c in ([] if FROM_RECORDS else sorted(refs.items())):
    v=known.get(ref,{})
    reason='Chưa đủ bằng chứng đã kiểm tra để kết luận trạng thái và chuỗi sửa đổi hiện hành. Xem nhật ký tìm kiếm; không suy ra còn hiệu lực từ việc chưa thấy văn bản thay thế.'
    if not re.search(r'\d{4}',ref): reason='Trích dẫn thiếu số hiệu/năm hoặc chỉ tên chuẩn mực; chưa định danh chắc chắn văn bản và phiên bản. '+reason
    if ref.startswith('Luật thuế'): reason='Ứng viên regex chưa được xác nhận là tên văn bản; giữ nguyên dấu vết nguồn để rà soát, không dùng làm căn cứ pháp lý.'
    sources=[{'url':u,'publisher':urlparse(u).hostname,'retrieved_at':'2026-10-11','authority':'official'} for u in v.get('urls',[])]
    rec={'ref':ref,'status':v.get('status','unknown'),'replaced_by':v.get('replaced_by'),'amended_by':v.get('amended_by',[]),
         'effective_from':v.get('effective_from'),'effective_date_meaning':'effective date of cited change, not necessarily original instrument',
         'scope':v.get('scope','UNKNOWN'),'key_changes':[{'text':v['note'],'source_url':v['urls'][0]}] if v and v['status']!='unknown' else [],
         'cited_in_courses':c['courses'],'curriculum_occurrences':c['occurrences'],'variants':c['variants'],
         'sources':sources,'evidence_status':'OBSERVED' if v and v['status']!='unknown' else 'UNKNOWN','layer':'external',
         'checked_at':'2026-10-11','unknown_reason':v.get('note',reason) if v.get('status','unknown')=='unknown' else None,
         'search_log':logs.get(ref),'record_kind':'verified_status' if v and v['status']!='unknown' else 'unverified_reference',
         'freshness_limit':'Snapshot of sources checked on the stated date; not a guarantee that every later amendment has been found.'}
    p=out/(slug(ref)+'.yaml'); p.write_text(yaml.safe_dump(rec,allow_unicode=True,sort_keys=False),encoding='utf-8')
    records.append((p,rec))
if FROM_RECORDS:
    # Wave 6: rebuild from reviewed records without overwriting them from the
    # historical Wave 5 verified_updates snapshot.
    records = [(p, yaml.safe_load(p.read_text(encoding='utf-8'))) for p in sorted(out.glob('*.yaml'))]
chunks=[]
def chunk(sid,text,rel,url,sha,page=None,role='regulation_status',status='OBSERVED'):
    chunks.append({'chunk_id':f'chk-{sid}-{len(chunks)+1:04d}','source_id':sid,'course_id':'external','course_name':'Quy định hiện hành (nguồn ngoài giáo trình)',
       'source_file':rel.split('/')[-1],'relative_path':rel,'source_type':'external','content_role':role,'authority':8,
       'chapter':None,'topic':None,'section':None,'page_start':page,'page_end':page,'page_range':str(page) if page else None,
       'text':text,'concept_ids':[],'parse_quality':'ok','evidence_status':status,'url':url,'provenance':{'source_sha256':sha}})
for p,rec in records:
    if rec['status']=='unknown': continue  # unknown metadata is not positive evidence
    text=f"{rec['ref']}\nTrạng thái: {rec['status']}. Thay bởi: {rec['replaced_by'] or '-'}; sửa bởi: {', '.join(rec['amended_by']) or '-'}.\nHiệu lực thay đổi: {rec['effective_from']}.\n{rec['scope']}\n"+'\n'.join(k['text'] for k in rec['key_changes'])
    # W6b review B1: keep the record's own evidence label; cite the first OFFICIAL source when there is one.
    _src=next((x for x in rec['sources'] if x.get('authority')=='official'),rec['sources'][0])
    chunk('ext-'+slug(rec['ref']),text,p.relative_to(R).as_posix(),_src['url'],hashlib.sha256(p.read_bytes()).hexdigest(),
          status=rec.get('evidence_status') or 'OBSERVED')
downloads=json.loads((R/'research/source_downloads.json').read_text(encoding='utf-8'))
for src in downloads:
    if src.get('download_status')=='unavailable': continue
    e=json.loads((R/src['extract']).read_text(encoding='utf-8'))
    assert e['ok'] and e['page_count']==len(e['pages'])
    for unit in pages_to_units(e['pages']):
        if len(unit['text'])>=80: chunk('ext-'+src['id'],unit['text'],src['path'],src['url'],src['sha256'],unit['page_start'],'official_text')
path=R/'data/chunks/external.chunks.jsonl'
path.write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in chunks),encoding='utf-8')
result=build_index(path,R/'data/indexes/3.0.0/external',meta_extra={'course_id':'external','index_version':'3.0.0','extract_version':'3.0.0','layer':'external'})
summary={'references':len(citations),'records':len(records),'verified':sum(r['status']!='unknown' for _,r in records),'unknown':sum(r['status']=='unknown' for _,r in records),'chunks':len(chunks),'downloaded_pdfs':sum('sha256' in d for d in downloads),'download_unavailable':sum(d.get('download_status')=='unavailable' for d in downloads)}
(R/'reports/v3/external_build.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(summary)
