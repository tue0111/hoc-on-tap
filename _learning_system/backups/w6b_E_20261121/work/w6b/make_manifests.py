import yaml,json,collections
def mk(cid,gate,extra):
    cov=json.load(open(f'data/normalized/{cid}.coverage.json',encoding='utf-8'))
    meta=json.load(open(f'data/indexes/3.0.0/{cid}/meta.json',encoding='utf-8'))
    con=yaml.safe_load(open(f'curriculum/concepts/{cid}.yaml',encoding='utf-8'))['concepts']
    chap=collections.defaultdict(set)
    for c in con:
        if c.get('chapter') is not None and c.get('topic'): chap[c['chapter']].add(str(c['topic']))
    reg=[c for c in yaml.safe_load(open('curriculum/course_registry.yaml',encoding='utf-8'))['courses'] if c['id']==cid][0]
    # Count per error type from the per-document file, not len(cov['errors']) (which mixes all error kinds).
    PPTX_ERR='pptx extractor not wired (non-learner pptx)'
    docs=[json.loads(l) for l in open(f'data/normalized/{cid}.documents.jsonl',encoding='utf-8') if l.strip()]
    pptx_n=sum(1 for d in docs if d.get('extract_error')==PPTX_ERR)
    other=[{'source_id':d['source_id'],'reason':d['extract_error']} for d in docs if d.get('extract_error') and d.get('extract_error')!=PPTX_ERR]
    if other: print('WARNING', cid, 'other extract errors:', other)
    m={'course_id':cid,'course_name':{'value':reg['name'],'evidence_status':'OBSERVED'},'course_codes':reg.get('codes') or [],
       'source_folder':'D:'+chr(92)+'Hoc'+chr(92)+reg['name'],
       'chapters_observed':[{'chapter':k,'topics':sorted(v)} for k,v in sorted(chap.items())],
       'coverage':{'documents':cov['document_count'],'pages':cov['page_count'],'indexed_documents':cov['indexed_documents'],
                   'pptx_not_extracted':pptx_n,'other_extract_errors':other,'note':'PPTX slides are not extracted (extractor not wired); each has a script PDF/DOCX for the same topic'},
       'v3':{'tier':'retrieval','index':'3.0.0','gate':gate,'chunk_count':meta['chunk_count'],'concepts':len(con),'built_by':'W6b'}}
    m.update(extra)
    open(f'curriculum/course_manifests/{cid}.yaml','w',encoding='utf-8').write('# Course manifest (W6b, 2026-11-21). Evidence labels: OBSERVED | INFERRED | UNKNOWN. Details: reports/v3/'+gate+'.md\n'+yaml.safe_dump(m,allow_unicode=True,sort_keys=False)); print(cid,meta['chunk_count'],len(con))
mk('ke-toan-tai-chinh-3','G-ke-toan-tai-chinh-3',{'code_official':'UNKNOWN','code_conflict':{'ACCO3310':'filenames, src-0592 p1','ACCO1335':'page 1 of chapter scripts','ACCO3301':'src-0595 p1'},
   'prerequisites':{'explicit_prerequisites':['ke-toan-tai-chinh-2'],'evidence_status':'OBSERVED','evidence':{'source_id':'src-0580','page':1,'quote':'Như các anh chị đã tìm hiểu sơ bộ ở chương Kế toán nợ phải trả, môn Kế toán tài chính 2, ...'},'kind':'prior-knowledge reference by the lecturer, not a syllabus prerequisite line; recorded with learner approval 2026-11-21'}})
mk('ke-toan-hanh-chinh-su-nghiep','G-ke-toan-hanh-chinh-su-nghiep',{'code_official':'UNKNOWN','note':'no course code in the materials','regulation_basis_observed':'TT 24/2024/TT-BTC (TT 107/2017 mentioned once, src-0409 p2)','prerequisites':{'explicit_prerequisites':[],'note':'no quotable statement found'}})
