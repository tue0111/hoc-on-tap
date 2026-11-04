# judgment step 6.5 for KTTC2: concept names/aliases chosen by the executor from headings; refs located mechanically.
import json, re, sys, yaml, unicodedata
sys.path.insert(0,'/home/claude/Hoc/_learning_system')
from retrieval.textutil import fold
PRE='ktcp'
pages=[json.loads(l) for l in open('data/normalized/ke-toan-chi-phi.pages.jsonl')]
idx=[p for p in pages if p['index_include']]
def slug(s):
    s=s.replace('đ','d').replace('Đ','D'); s=unicodedata.normalize('NFD',s); s=''.join(c for c in s if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
# (canonical, aliases, chapter, topic, same_as, extra_chapters)
S=[
("Khái niệm và vai trò của kế toán chi phí",["kế toán quản trị","kế toán tài chính"],1,"1.1",None,None),
("Yếu tố thành công cốt lõi",["yếu tố thành công"],1,"1.2",None,None),
("Phân tích chuỗi giá trị",["chuỗi giá trị","hoạt động tạo ra giá trị"],1,"1.2",None,None),
("Chi phí sản xuất chung",[],2,"2.1.1",None,None),
("Đối tượng chịu chi phí",["đối tượng tính giá thành"],2,"2.1.1","doi-tuong-chiu-chi-phi",None),
("Chi phí trực tiếp",[],2,"2.1.1","chi-phi-truc-tiep",None),
("Chi phí gián tiếp",[],2,"2.1.1","chi-phi-gian-tiep",None),
("Biến phí và định phí",["biến phí","định phí","chi phí hỗn hợp","ứng xử của chi phí","mức độ hoạt động"],2,"2.1.2",None,None),
("Chi phí sản phẩm và chi phí thời kỳ",["chi phí sản phẩm","chi phí thời kỳ","chi phí ngoài sản xuất"],2,"2.1.2",None,None),
("Chi phí chuyển đổi",[],2,"2.1.2",None,[4,6]),
("Giá thành sản phẩm",["giá thành toàn bộ"],2,"2.2","gia-thanh",[7]),
("Kế toán chi phí theo công việc",["kỳ tính giá thành"],3,"3.1","ktcp-theo-cong-viec",None),
("Chi phí thực tế kết hợp với chi phí ước tính",["chi phí thực tế kết hợp","phân bổ thiếu"],3,"3.2",None,None),
("Kế toán chi phí theo quy trình",["báo cáo chi phí sản xuất","quy trình sản xuất liên tục"],4,"4.1.1","ktcp-theo-quy-trinh",None),
("Sản phẩm dở dang cuối kỳ",["sản phẩm dở dang"],4,"4.1.1",None,[5,6]),
("Sản lượng tương đương",["sản lượng tương đương"],4,"4.1.1",None,None),
("Phương pháp trung bình",[],4,"4.1.2",None,None),
("Phương pháp FIFO",["FIFO","nhập trước xuất trước"],4,"4.1.3",None,None),
("2 giai đoạn",["hai giai đoạn"],4,"4.2",None,None),
("Chi phí sản xuất chung ước tính",[],4,"4.3.1",None,None),
("Xử lý chênh lệch",[],4,"4.3.2",None,None),
("Kế toán chi phí định mức",["chi phí định mức","định mức chi phí"],5,"5.1","ktcp-dinh-muc",None),
("Trình tự kế toán chi phí định mức",[],5,"5.2",None,None),
("Phân bổ chi phí sản xuất chung",[],6,"6.1","phan-bo-chi-phi",None),
("Phương pháp ABC",["phương pháp ABC","nhân tố phát sinh chi phí","cost driver"],6,"6.1",None,None),
("Phân bổ chi phí bộ phận phục vụ",["bộ phận phục vụ","phương pháp trực tiếp","phương pháp bậc thang"],6,"6.2",None,None),
("Thiệt hại trong sản xuất",["thiệt hại trong sản xuất","sản phẩm hỏng","phế liệu","hỏng ngoài định mức"],6,"6.2",None,None),
("Môi trường vừa theo công việc",[],6,"6.3",None,None),
("Phương pháp giá thành khả biến và giá thành sản xuất",["giá thành khả biến","giá thành sản xuất"],7,"7.1","ktcp-gia-thanh-quyet-dinh",None),
("Báo cáo thu nhập",["điểm hòa vốn"],7,"7.2",None,None),
]
T=lambda s: fold(re.sub(r'\s+',' ',s))
ptext=[(p,T(p['text'])) for p in idx]
concepts=[];dropped=[]
for name,al,ch,tp,same,extra in S:
    cid=f"{PRE}-{slug(name)}"
    keep=[]
    for a in al:
        fa=T(a)
        present=any(fa in t for _,t in ptext)
        ok_len=len(fa)>=6 or (a.isupper() and present)
        if present and ok_len: keep.append(a)
        else: dropped.append((cid,a))
    if not any(T(name) in t for _,t in ptext) and not keep:
        dropped.append((cid,'CANONICAL ABSENT:'+name)); continue
    refs=[];cands=[T(name)]+[T(a) for a in keep]
    # prefer pages from unit of same topic
    pref=sorted(ptext,key=lambda x:(x[0]['topic']!=tp, x[0]['page']))
    for p,t in pref:
        if any(c in t for c in cands):
            refs.append({'source_id':p['source_id'],'page':p['page']})
            if len(refs)==2:break
    concepts.append({'concept_id':cid,'canonical_name':name,'aliases':keep,'same_as':same,'chapter':ch,'topic':tp,
        **({'chapters':extra} if extra else {}),'source_refs':refs,'evidence_status':'OBSERVED','confidence':'high' if refs else 'low'})
ids={c['canonical_name']:c['concept_id'] for c in concepts}
cand={a['account'] for a in json.load(open('work/ke-toan-chi-phi/concept_candidates.json'))['accounts'] if a['count']>=2}
AM={'154':"Kế toán chi phí theo công việc",'621':"Chi phí sản xuất chung",'622':"Chi phí sản xuất chung",'627':"Chi phí sản xuất chung",
 '155':"Giá thành sản phẩm",'632':"Giá thành sản phẩm",'152':"Kế toán chi phí định mức"}
amap={a:ids[n] for a,n in AM.items() if a in cand and n in ids}
doc={'course_id':'ke-toan-chi-phi','version':'0.1.0','id_prefix':PRE,'concepts':concepts,'account_map':amap,'edges':[],'conflicts':[]}
yaml.safe_dump(doc,open('curriculum/concepts/ke-toan-chi-phi.yaml','w',encoding='utf-8'),allow_unicode=True,sort_keys=False,width=120)
print(len(concepts),'concepts',len(amap),'accounts; dropped:',dropped)
