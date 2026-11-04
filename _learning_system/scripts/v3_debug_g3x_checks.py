"""Additional behavior checks independent of the frozen G3x questions."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from retrieval.partition import _bigram_cov, _evidence_tokens, resolve_extended_scope
from retrieval.retrieve import retrieve

def main():
    assert _bigram_cov(_evidence_tokens('hướng dẫn hạch toán tiền gửi'), ['hạch toán tiền gửi']) == 1.0
    assert resolve_extended_scope('So sánh Ngân hàng thương mại và Tài chính hành chính sự nghiệp') is None
    assert resolve_extended_scope('Tài chính hành chính sự nghiệp: ngân hàng thương mại', {'course_id':'ngan-hang-thuong-mai'})['course_id'] == 'ngan-hang-thuong-mai'
    assert retrieve('Kế toán chi phí: giá thành theo quy trình')['unknowns'] == ['course_not_indexed']
    cases = [
        ('ke-toan-tai-chinh-2', 'Chiết khấu thương mại'),
        ('ke-toan-tai-chinh-2', 'Cổ tức bằng cổ phiếu'),
        ('ke-toan-tai-chinh-2', 'Trái phiếu'),
        ('kiem-toan-1', 'Rủi ro kiểm toán'),
        ('kinh-doanh-va-nghiep-vu', 'Văn hóa tổ chức'),
        ('tai-chinh-hanh-chinh-su-nghiep', 'Quỹ tiền lương'),
    ]
    for cid, question in cases:
        pkg = retrieve(question, {'course_id':cid})
        print(cid, question, pkg['coverage'], pkg['unknowns'])
        assert pkg['coverage'] != 'insufficient', (cid, question)
        assert all(it['course_id'] == cid for it in pkg['items'])
    print('BEHAVIOR_CHECKS PASS')

if __name__ == '__main__':
    main()
