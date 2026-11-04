# judgment step 6.5 for KTTC2: concept names/aliases chosen by the executor from headings; refs located mechanically.
import json, re, sys, yaml, unicodedata
sys.path.insert(0,'/home/claude/Hoc/_learning_system')
from retrieval.textutil import fold
PRE='kt1'
pages=[json.loads(l) for l in open('data/normalized/kiem-toan-1.pages.jsonl')]
idx=[p for p in pages if p['index_include']]
def slug(s):
    s=s.replace('đ','d').replace('Đ','D'); s=unicodedata.normalize('NFD',s); s=''.join(c for c in s if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
# (canonical, aliases, chapter, topic, same_as, extra_chapters)
S=[
("Giả định hoạt động liên tục",[],1,"1.1",None,[6]),
("Cơ sở dồn tích",[],1,"1.1","co-so-don-tich",None),
("Đặc điểm chất lượng",[],1,"1.2",None,None),
("Trung thực và hợp lý",["trung thực hợp lý"],1,"1.2",None,[2,4,6]),
("Ghi nhận và đánh giá các yếu tố",["ghi nhận và đánh giá"],1,"1.3",None,None),
("Khái niệm kiểm toán",["phân loại kiểm toán"],2,"2.1","kiem-toan",None),
("Kiểm toán nhà nước",[],2,"2.1",None,None),
("Kiểm toán nội bộ",[],2,"2.1",None,None),
("Kiểm toán độc lập",[],2,"2.1",None,None),
("Kiểm toán báo cáo tài chính",[],2,"2.1",None,None),
("Kiểm toán hoạt động",[],2,"2.1",None,None),
("Kiểm toán tuân thủ",[],2,"2.1",None,None),
("Quy trình kiểm toán",[],2,"2.2",None,None),
("Môi trường kiểm toán",[],2,"2.3",None,None),
("Chuẩn mực kiểm toán",[],2,"2.3",None,None),
("Đạo đức nghề nghiệp",["tính độc lập","tính khách quan"],2,"2.3","dao-duc-nghe-nghiep-ke-toan",None),
("Kiểm soát nội bộ",[],3,"3.1","kiem-soat-noi-bo",None),
("Môi trường kiểm soát",[],3,"3.2",None,None),
("Hoạt động kiểm soát",[],3,"3.2",None,None),
("Thông tin và truyền thông",[],3,"3.2",None,None),
("COSO",[],3,"3.2",None,None),
("Tìm hiểu và đánh giá",[],3,"3.3",None,None),
("Trọng yếu",["mức trọng yếu"],4,"4.1","trong-yeu-kiem-toan",None),
("Trọng yếu thực hiện",[],4,"4.1",None,None),
("Rủi ro kiểm toán",["mô hình rủi ro"],4,"4.2","rui-ro-kiem-toan",None),
("Rủi ro tiềm tàng",[],4,"4.2",None,None),
("Rủi ro kiểm soát",[],4,"4.2",None,None),
("Rủi ro phát hiện",[],4,"4.2",None,None),
("Tiền kế hoạch",[],4,"4.3",None,None),
("Lập kế hoạch kiểm toán",["chiến lược kiểm toán"],4,"4.3",None,None),
("Hợp đồng kiểm toán",[],4,"4.3",None,None),
("Bằng chứng kiểm toán",["thu thập bằng chứng"],5,"5.1","bang-chung-kiem-toan",None),
("Cơ sở dẫn liệu",[],5,"5.2",None,None),
("Kỹ thuật thu thập bằng chứng kiểm toán",["tính toán lại","thực hiện lại","kiểm tra tài liệu"],5,"5.3",None,None),
("Thủ tục phân tích",[],5,"5.3",None,None),
("Kiểm tra chi tiết",[],5,"5.3",None,None),
("Đánh giá tổng thể",[],6,"6.1",None,None),
("Hoàn thành kiểm toán",["báo cáo kiểm toán"],6,"6.2","hoan-thanh-kiem-toan",None),
("Ý kiến kiểm toán",["ý kiến chấp nhận toàn phần","từ chối đưa ra ý kiến"],6,"6.3",None,None),
("Gian lận",[],3,"3.1","gian-lan-bctc",[1,2,4,6]),
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
doc={'course_id':'kiem-toan-1','version':'0.1.0','id_prefix':PRE,'concepts':concepts,'account_map':{},'edges':[],'conflicts':[
 {'type':'TITLE_VARIANT','note':'Chương 6: script/slide "Hoàn thành kiểm toán" vs hướng dẫn ôn tập/outline "Báo cáo kiểm toán"; both kept as names of the same chapter concept','source_ids':['src-0195','src-0196'],'evidence_status':'OBSERVED'}]}
yaml.safe_dump(doc,open('curriculum/concepts/kiem-toan-1.yaml','w',encoding='utf-8'),allow_unicode=True,sort_keys=False,width=120)
print(len(concepts),'concepts; dropped:',dropped)
