"""Fetch only public official downloads; preserve originals and record hashes."""
import json,hashlib,sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests
import urllib.request
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R))
from scripts.phase2_extract import extract_pdf
BASE='https://congbao.chinhphu.vn/van-ban/thong-tu-so-99-2025-tt-btc-46529.htm'
dest=R/'research/sources'; dest.mkdir(exist_ok=True)
response=requests.get(BASE,timeout=30); response.raise_for_status()
links=[a['href'] for a in BeautifulSoup(response.text,'html.parser').find_all('a',href=True) if '.pdf' in a.get_text()]
assert len(links)==10
jobs=[(f'tt99-2025-part{i:02}',url,BASE) for i,url in enumerate(links,1)]
jobs.append(('luat76-2025','https://datafiles.chinhphu.vn/cpp/files/vbpq/2025/7/76-2025-qh15.pdf','https://chinhphu.vn/?docid=214562&pageid=27160'))
def fetch(job):
    name,url,page=job; path=dest/(name+'.pdf')
    if not path.exists():
        # urllib uses the Windows trust store; certificate verification remains on.
        try:
            with urllib.request.urlopen(url,timeout=45) as response:
                data=response.read()
        except Exception as exc:
            print('DOWNLOAD_UNAVAILABLE',name,str(exc),flush=True)
            return {'id':name,'url':url,'landing_url':page,'download_status':'unavailable','reason':str(exc)}
        if not data.startswith(b'%PDF'): raise ValueError('Not PDF: '+name)
        path.write_bytes(data)
    sha=hashlib.sha256(path.read_bytes()).hexdigest()
    out=dest/(name+'.extracted.json')
    if out.exists(): e=json.loads(out.read_text(encoding='utf-8'))
    else:
        e=extract_pdf(path)
        if not e['ok']: raise ValueError(str(e['error']))
        out.write_text(json.dumps(e,ensure_ascii=False),encoding='utf-8')
    from pypdf import PdfReader
    assert len(PdfReader(path).pages)==e['page_count']==len(e['pages'])
    print(name,e['page_count'],e['char_count'],flush=True)
    return {'id':name,'url':url,'landing_url':page,'path':path.relative_to(R).as_posix(),'extract':out.relative_to(R).as_posix(),'sha256':sha,'pages':e['page_count'],'chars':e['char_count'],'retrieved_at':'2026-10-11','authority':'official'}
with ThreadPoolExecutor(max_workers=3) as pool: records=list(pool.map(fetch,jobs))
(R/'research/source_downloads.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
