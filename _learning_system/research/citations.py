"""Conservative citation parser shared by harvest and runtime matching."""
import re,unicodedata
PATTERNS=[
 r'(?:Thông\s+tư|TT)\s*(\d+)\s*/\s*(\d{4})(?:\s*/\s*(TT-[A-ZĐ]+))?',
 r'Nghị\s+định\s*(\d+)\s*/\s*(\d{4})\s*/\s*NĐ-CP',
 r'(?:Luật\s+[^\n,.;]{0,60}?)?(\d+)\s*/\s*(\d{4})\s*/\s*QH(\d+)',
 r'Quyết\s+định\s*(\d+)\s*/\s*(\d{4})\s*/\s*QĐ-([A-Z]+)',
 r'(?:VAS\s*|Chuẩn\s+mực\s+kế\s+toán\s+(?:Việt\s+Nam\s+)?số\s*)(\d+)',
 r'(IFRS|IAS)\s*(\d+)',
 r'Luật\s+(Kế\s+toán|Doanh\s+nghiệp|Các\s+tổ\s+chức\s+tín\s+dụng|Kiểm\s+toán\s+độc\s+lập|Ngân\s+sách\s+nhà\s+nước|Chứng\s+khoán|Thuế[^\n,.;]{2,30})(?:\s+năm\s*(\d{4}))?'
]
def references(text):
    text=unicodedata.normalize('NFC',text)
    out=[]
    for i,pat in enumerate(PATTERNS):
        for m in re.finditer(pat,text,re.I):
            if i==0: ref=f'Thông tư {int(m[1])}/{m[2]}'+('/'+m[3].upper() if m[3] else '')
            elif i==1: ref=f'Nghị định {int(m[1])}/{m[2]}/NĐ-CP'
            elif i==2: ref=f'Luật {int(m[1])}/{m[2]}/QH{m[3]}'
            elif i==3: ref=f'Quyết định {int(m[1])}/{m[2]}/QĐ-{m[3].upper()}'
            elif i==4: ref=f'VAS {int(m[1])}'
            elif i==5: ref=f'{m[1].upper()} {int(m[2])}'
            else: ref='Luật '+' '.join(m[1].lower().split())+(f' năm {m[2]}' if m[2] else '')
            # W6b G17: drop harvest truncation marks (ellipsis) so truncated variants merge; raw match kept as variant.
            ref=re.sub(r'[\s….]+$','',ref)
            out.append((ref,m[0]))
    return out
def slug(ref):
    s=unicodedata.normalize('NFD',ref.lower().replace('đ','d'))
    return re.sub('[^a-z0-9]+','-', ''.join(c for c in s if not unicodedata.combining(c))).strip('-')
