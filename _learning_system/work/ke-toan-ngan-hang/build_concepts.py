# judgment step 6.5 for KTTC2: concept names/aliases chosen by the executor from headings; refs located mechanically.
import json, re, sys, yaml, unicodedata
sys.path.insert(0,'/home/claude/Hoc/_learning_system')
from retrieval.textutil import fold
PRE='ktnh'
pages=[json.loads(l) for l in open('data/normalized/ke-toan-ngan-hang.pages.jsonl')]
idx=[p for p in pages if p['index_include']]
def slug(s):
    s=s.replace('đ','d').replace('Đ','D'); s=unicodedata.normalize('NFD',s); s=''.join(c for c in s if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
# (canonical, aliases, chapter, topic, same_as, extra_chapters)
S=[
("Đặc điểm kinh doanh của ngân hàng",[],1,"1.1",None,None),
("Đối tượng kế toán ngân hàng",[],1,"1.2",None,None),
("Tổ chức công tác kế toán ngân hàng",[],1,"1.3",None,None),
("Hệ thống tài khoản kế toán ngân hàng",["hệ thống tài khoản kế toán các tổ chức tín dụng"],1,"1.4","he-thong-tk-ngan-hang",None),
("Chứng từ kế toán",[],1,"1.5",None,None),
("Kế toán nghiệp vụ tiền mặt",["tiền mặt tại đơn vị","thu/chi tiền mặt"],2,"2.1",None,None),
("Tiền gửi tại Ngân hàng Nhà nước",["tiền gửi tại tổ chức tín dụng"],2,"2.2",None,None),
("Nguồn huy động vốn",["huy động vốn"],3,"3.1","huy-dong-von",None),
("Tiền gửi tiết kiệm",[],3,"3.2",None,None),
("Phát hành giấy tờ có giá",["giấy tờ có giá","chiết khấu giấy tờ có giá"],3,"3.3",None,None),
("Hình thức thanh toán không dùng tiền mặt",[],4,"4.1",None,None),
("Phương thức thanh toán qua ngân hàng",["ủy nhiệm chi"],4,"4.2",None,None),
("Hệ thống thanh toán qua ngân hàng",[],4,"4.3",None,None),
("Thanh toán liên ngân hàng",["thanh toán bù trừ"],4,"4.5",None,None),
("Cấp tín dụng",[],5,"5.1","cap-tin-dung",None),
("Nghiệp vụ cho vay",["nợ trong hạn","hợp đồng tín dụng"],5,"5.2","cho-vay",None),
("Nghiệp vụ tín dụng khác",["bảo lãnh ngân hàng"],5,"5.3",None,None),
("Đầu tư và kinh doanh chứng khoán",[],6,"6.1","ktnh-dau-tu-chung-khoan",None),
("Chứng khoán kinh doanh",[],6,"6.2",None,None),
("Chứng khoán sẵn sàng để bán",[],6,"6.3",None,None),
("Chứng khoán giữ đến ngày đáo hạn",[],6,"6.4",None,None),
("Kinh doanh ngoại tệ và thanh toán quốc tế",[],7,"7.1","ktnh-ngoai-te",None),
("Mua bán ngoại tệ giao ngay",[],7,"7.2",None,None),
("Giao dịch tiền tệ kỳ hạn",["forward"],7,"7.3",None,None),
("Thanh toán quốc tế chuyển tiền và nhờ thu",["nhờ thu"],7,"7.4",None,None),
("Tín dụng chứng từ",["thư tín dụng"],7,"7.5",None,None),
("Thu nhập và chi phí",[],8,"8.1",None,None),
("Kế toán thu nhập",[],8,"8.2",None,None),
("Xác định kết quả kinh doanh",[],8,"8.4",None,None),
("Trình bày báo cáo tài chính trong ngân hàng thương mại",["bảng cân đối kế toán","báo cáo kết quả hoạt động kinh doanh"],9,"9.1","ktnh-bctc-ngan-hang",None),
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
cand={a['account'] for a in json.load(open('work/ke-toan-ngan-hang/concept_candidates.json'))['accounts'] if a['count']>=2}
G={"Kế toán nghiệp vụ tiền mặt":"101 1011 1013 1019 3614 461","Tiền gửi tại Ngân hàng Nhà nước":"111 1113 1311 1312 1331",
"Tiền gửi tiết kiệm":"4211 4221 4232 4913","Phát hành giấy tờ có giá":"431 432 433 4921 803",
"Phương thức thanh toán qua ngân hàng":"4271 5191 5192 4599","Thanh toán liên ngân hàng":"5012",
"Nghiệp vụ cho vay":"2111 2112 2192 221 3941 702","Nghiệp vụ tín dụng khác":"925 994 387",
"Đầu tư và kinh doanh chứng khoán":"392 703","Chứng khoán kinh doanh":"153 741 841","Chứng khoán sẵn sàng để bán":"3922","Chứng khoán giữ đến ngày đáo hạn":"163 3923",
"Kinh doanh ngoại tệ và thanh toán quốc tế":"1031 6311 821","Mua bán ngoại tệ giao ngay":"4711 4712","Giao dịch tiền tệ kỳ hạn":"4741 4742 4861 4862 723 823 6322 6332",
"Thanh toán quốc tế chuyển tiền và nhờ thu":"455 9122 9123 9124","Tín dụng chứng từ":"4282",
"Thu nhập và chi phí":"488 388","Kế toán thu nhập":"711 801","Xác định kết quả kinh doanh":"691 692 4534"}
amap={}
for n,accs in G.items():
    for a in accs.split():
        if a in cand and n in ids: amap[a]=ids[n]
doc={'course_id':'ke-toan-ngan-hang','version':'0.1.0','id_prefix':PRE,'concepts':concepts,'account_map':amap,'edges':[],'conflicts':[
 {'type':'SOURCE_VINTAGE','note':'src-0047 chart of accounts is from QĐ 479/2004/QĐ-NHNN (labelled tài liệu tham khảo); current status to be checked in Wave 5','source_ids':['src-0047'],'evidence_status':'OBSERVED'}]}
yaml.safe_dump(doc,open('curriculum/concepts/ke-toan-ngan-hang.yaml','w',encoding='utf-8'),allow_unicode=True,sort_keys=False,width=120)
print(len(concepts),'concepts',len(amap),'accounts; dropped:',dropped)
