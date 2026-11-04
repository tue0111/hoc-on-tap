"""Run frozen suites with candidate tiers in memory; never alter frozen inputs."""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from retrieval import courses as C
from retrieval.config import SYSTEM
from scripts import v3_eval_course as evaluator

TARGETS = ['ke-toan-tai-chinh-2', 'kiem-toan-1', 'kinh-doanh-va-nghiep-vu',
           'luat-kinh-doanh', 'ngan-hang-thuong-mai', 'thi-truong-tai-chinh',
           'tai-chinh-hanh-chinh-su-nghiep']

if __name__ == '__main__':
    frozen = json.loads((SYSTEM / 'evals/v3/FROZEN.json').read_text(encoding='utf-8'))
    for entry in frozen.values():
        assert hashlib.sha256((SYSTEM / entry['file']).read_bytes()).hexdigest() == entry['sha256']
    for course in C.load_registry()['courses']:
        if course['id'] in TARGETS:
            course['tier'] = 'retrieval'
    for cid in TARGETS:
        print('COURSE', cid, flush=True)
        sys.argv = ['v3_eval_course', '--course', cid, '--tag', '_debug_fix']
        evaluator.main()
