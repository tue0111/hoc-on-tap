# judgment step 6.5 for KTTC2: concept names/aliases chosen by the executor from headings; refs located mechanically.
import json, re, sys, yaml, unicodedata
sys.path.insert(0,'/home/claude/Hoc/_learning_system')
from retrieval.textutil import fold
PRE='kttc2'
pages=[json.loads(l) for l in open('data/normalized/ke-toan-tai-chinh-2.pages.jsonl')]
idx=[p for p in pages if p['index_include']]
def slug(s):
    s=s.replace('đ','d').replace('Đ','D'); s=unicodedata.normalize('NFD',s); s=''.join(c for c in s if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
# (canonical, aliases, chapter, topic, same_as, extra_chapters)
S=[
("Tài sản cố định",["TSCĐ"],1,"1.1","tscd",None),
("Khái niệm và nguyên tắc tài sản cố định hữu hình",["tài sản cố định hữu hình","TSCĐ hữu hình","nguyên giá tài sản cố định"],1,"1.1",None,None),
("Khái niệm và nguyên tắc tài sản cố định vô hình",["tài sản cố định vô hình","TSCĐ vô hình","quyền sử dụng đất"],1,"1.2",None,None),
("Các phương pháp tính khấu hao TSCĐ",["phương pháp khấu hao","khấu hao đường thẳng","số dư giảm dần","khấu hao theo sản lượng","phương pháp sản lượng"],1,"1.3",None,None),
("Khấu hao tài sản cố định",["khấu hao","hao mòn tài sản cố định"],1,"1.3","khau-hao",None),
("Kế toán tăng tài sản cố định",["tăng TSCĐ","mua sắm tài sản cố định","xây dựng cơ bản dở dang"],1,"1.4",None,None),
("Kế toán giảm tài sản cố định",["giảm TSCĐ","thanh lý tài sản cố định","nhượng bán tài sản cố định","thanh lý TSCĐ","nhượng bán TSCĐ"],1,"1.5",None,None),
("Kế toán chi phí phát sinh sau khi ghi nhận ban đầu",["chi phí phát sinh sau ghi nhận ban đầu","sửa chữa lớn","nâng cấp tài sản cố định"],1,"1.6",None,None),
("Trình bày thông tin trên báo cáo tài chính",["trình bày thông tin","thuyết minh báo cáo tài chính"],1,"1.7","bao-cao-tai-chinh",[1,2,3,4]),
("Khái niệm, điều kiện ghi nhận và phân loại",["điều kiện ghi nhận nợ phải trả","phân loại nợ phải trả"],2,"2.1",None,None),
("Nợ phải trả",["khoản nợ phải trả","nợ ngắn hạn","nợ dài hạn"],2,"2.1","no-phai-tra",None),
("Ghi nhận và đánh giá nợ phải trả",["đánh giá nợ phải trả","ghi nhận nợ phải trả"],2,"2.2",None,None),
("Phải trả cho người bán",["tài khoản 331","phải trả người bán"],2,"2.3",None,None),
("Các khoản đi vay",["tài khoản 3411","vay và nợ thuê tài chính"],2,"2.3",None,None),
("Chi phí phải trả",["tài khoản 335","trích trước chi phí"],2,"2.3",None,None),
("Thuế và các khoản phải nộp nhà nước",["tài khoản 333","thuế phải nộp"],2,"2.4",None,None),
("Thuế giá trị gia tăng",["thuế GTGT","thuế giá trị gia tăng phải nộp","thuế giá trị gia tăng được khấu trừ"],2,"2.4",None,None),
("Phải trả người lao động",["tiền lương và các khoản trích theo lương","tài khoản 334","bảo hiểm xã hội","bảo hiểm y tế","bảo hiểm thất nghiệp","kinh phí công đoàn"],2,"2.5",None,None),
("Quỹ khen thưởng, phúc lợi",["quỹ khen thưởng phúc lợi","tài khoản 353"],2,"2.5",None,None),
("Phải trả nội bộ",["tài khoản 336"],2,"2.6",None,None),
("Dự phòng phải trả",["tài khoản 352"],2,"2.6",None,None),
("Doanh thu chưa thực hiện",["tài khoản 3387"],2,"2.6",None,None),
("Vốn chủ sở hữu",["VCSH","các bộ phận cấu thành nên vốn chủ sở hữu"],3,"3.1","von-chu-so-huu",None),
("Kế toán vốn đầu tư của chủ sở hữu",["vốn góp của chủ sở hữu","thặng dư vốn cổ phần","vốn đầu tư của chủ sở hữu"],3,"3.2",None,None),
("Kế toán cổ phiếu quỹ",["cổ phiếu quỹ","tài khoản 419"],3,"3.3",None,None),
("Kế toán lợi nhuận chưa phân phối và các quỹ dự trữ",["lợi nhuận chưa phân phối","quỹ dự trữ","tài khoản 421"],3,"3.4",None,None),
("Định nghĩa và điều kiện ghi nhận",["điều kiện ghi nhận doanh thu","điều kiện ghi nhận chi phí","định nghĩa doanh thu"],4,"4.1",None,None),
("Kế toán doanh thu bán hàng",["giá vốn hàng bán","doanh thu cung cấp dịch vụ","doanh thu bán hàng","tài khoản 511","tài khoản 632"],4,"4.2",None,None),
("Kế toán hoạt động tài chính",["doanh thu hoạt động tài chính","chi phí tài chính","tài khoản 515","tài khoản 635"],4,"4.3",None,None),
("Kế toán chi phí hoạt động",["chi phí bán hàng","chi phí quản lý doanh nghiệp","tài khoản 641","tài khoản 642"],4,"4.4",None,None),
("Kế toán hoạt động khác",["thu nhập khác","chi phí khác","tài khoản 711","tài khoản 811"],4,"4.5",None,None),
("Kế toán xác định kết quả hoạt động kinh doanh",["xác định kết quả kinh doanh","tài khoản 911","kết chuyển doanh thu và chi phí"],4,"4.6","kttc2-xac-dinh-kqkd",None),
("Sự khác biệt giữa kế toán và thuế",["chênh lệch tạm thời","thuế thu nhập hoãn lại","chi phí không được trừ"],4,"4.8",None,None),
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
def cid(n): return ids[n]
AM={ '211':"Khái niệm và nguyên tắc tài sản cố định hữu hình",'213':"Khái niệm và nguyên tắc tài sản cố định vô hình",
 '214':"Khấu hao tài sản cố định",'2141':"Khấu hao tài sản cố định",'2411':"Kế toán tăng tài sản cố định",'2412':"Kế toán tăng tài sản cố định",
 '2413':"Kế toán chi phí phát sinh sau khi ghi nhận ban đầu",'331':"Phải trả cho người bán",'3411':"Các khoản đi vay",'335':"Chi phí phải trả",
 '333':"Thuế và các khoản phải nộp nhà nước",'3331':"Thuế giá trị gia tăng",'33311':"Thuế giá trị gia tăng",'133':"Thuế giá trị gia tăng",'1331':"Thuế giá trị gia tăng",'1332':"Thuế giá trị gia tăng",
 '3332':"Thuế và các khoản phải nộp nhà nước",'3333':"Thuế và các khoản phải nộp nhà nước",'3334':"Thuế và các khoản phải nộp nhà nước",'3335':"Thuế và các khoản phải nộp nhà nước",
 '334':"Phải trả người lao động",'3382':"Phải trả người lao động",'3383':"Phải trả người lao động",'3384':"Phải trả người lao động",'3386':"Phải trả người lao động",'353':"Quỹ khen thưởng, phúc lợi",
 '336':"Phải trả nội bộ",'352':"Dự phòng phải trả",'3387':"Doanh thu chưa thực hiện",'411':"Kế toán vốn đầu tư của chủ sở hữu",'4111':"Kế toán vốn đầu tư của chủ sở hữu",'4112':"Kế toán vốn đầu tư của chủ sở hữu",
 '419':"Kế toán cổ phiếu quỹ",'421':"Kế toán lợi nhuận chưa phân phối và các quỹ dự trữ",'414':"Kế toán lợi nhuận chưa phân phối và các quỹ dự trữ",'418':"Kế toán lợi nhuận chưa phân phối và các quỹ dự trữ",
 '511':"Kế toán doanh thu bán hàng",'521':"Kế toán doanh thu bán hàng",'632':"Kế toán doanh thu bán hàng",'515':"Kế toán hoạt động tài chính",'635':"Kế toán hoạt động tài chính",
 '641':"Kế toán chi phí hoạt động",'642':"Kế toán chi phí hoạt động",'711':"Kế toán hoạt động khác",'811':"Kế toán hoạt động khác",'911':"Kế toán xác định kết quả hoạt động kinh doanh",
 '8211':"Sự khác biệt giữa kế toán và thuế"}
cand={a['account'] for a in json.load(open('work/ke-toan-tai-chinh-2/concept_candidates.json'))['accounts'] if a['count']>=2}
amap={a:cid(n) for a,n in AM.items() if a in cand and n in ids}
doc={'course_id':'ke-toan-tai-chinh-2','version':'0.1.0','id_prefix':PRE,'concepts':concepts,'account_map':amap,'edges':[],'conflicts':[
 {'type':'COURSE_CODE','note':'ACCO1334 (script header) vs ACCO2315 (Hướng dẫn ôn tập header); official code UNKNOWN','source_ids':['src-0306','src-0305'],'evidence_status':'OBSERVED'}]}
yaml.safe_dump(doc,open('curriculum/concepts/ke-toan-tai-chinh-2.yaml','w',encoding='utf-8'),allow_unicode=True,sort_keys=False,width=120)
print(len(concepts),'concepts',len(amap),'accounts; dropped:',dropped)
