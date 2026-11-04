"""Approved G6 RAM-only simulation. Genuine PDF extraction and lexical index;
filesystem/transport are injected. No simulated source is created on D:.
"""
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.v3_refresh import compare, append_records, classify_source, guard, safe_relative, digest
from scripts.v3_inventory import active_records
from retrieval.config import SYSTEM, SOURCE_ROOT
from retrieval.chunking import pages_to_units
from retrieval.textutil import tokenize
import retrieval.index as lexical
import scripts.phase2_extract as extractor


class MemoryPath:
    files = {}

    def __init__(self, path):
        self.path = str(path)

    def __str__(self):
        return self.path

    def __truediv__(self, name):
        return MemoryPath(self.path + '/' + str(name))

    def mkdir(self, **kwargs):
        pass

    def read_text(self, **kwargs):
        return self.files[self.path]

    def write_text(self, text, **kwargs):
        self.files[self.path] = text
        return len(text)

    def open(self, mode='r', **kwargs):
        if 'w' not in mode:
            return io.StringIO(self.files[self.path])
        key = self.path

        class Writer(io.StringIO):
            def close(stream):
                MemoryPath.files[key] = stream.getvalue()
                super().close()

        return Writer()


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.row = {'source_id': 'src-0001', 'relative_path': 'Kế toán chi phí/Chương 1.pdf',
                    'course_id': 'ke-toan-chi-phi', 'size_bytes': 10, 'sha256': 'old'}

    def test_noop(self):
        self.assertEqual(compare([self.row], [self.row]), {'NEW': [], 'CHANGED': [], 'MISSING': []})

    def test_revision_append_and_replay(self):
        changed = {**self.row, 'size_bytes': 11, 'sha256': 'new'}
        delta = compare([changed], [self.row])
        new = append_records([self.row], [{**changed, 'supersedes': delta['CHANGED'][0]['supersedes']}])
        self.assertEqual(new[0], self.row)
        self.assertEqual(new[1]['source_id'], 'src-0002')
        self.assertEqual(active_records(new), [new[1]])
        self.assertEqual(compare([changed], new)['CHANGED'], [])

    def test_missing_preserved(self):
        delta = compare([], [self.row])
        self.assertEqual(delta['MISSING'], [self.row])
        with self.assertRaisesRegex(ValueError, 'MISSING'):
            guard(delta)

    def test_core_stops(self):
        for kind in ('NEW', 'CHANGED', 'MISSING'):
            delta = {k: [] for k in ('NEW', 'CHANGED', 'MISSING')}
            delta[kind] = [{'relative_path': 'Kế toán tài chính 1/new.pdf'}]
            with self.assertRaisesRegex(ValueError, 'OPUS_ONLY'):
                guard(delta)

    def test_classification(self):
        for rel, first in [('Kế toán chi phí/Claude outputs/x.pdf', ''),
                           ('Kế toán chi phí/x.pdf', 'Nguyễn Đức Tuệ'),
                           ('Kế toán chi phí/x.pdf', 'Họ tên sinh viên')]:
            self.assertEqual(classify_source(rel, first)['partition'], 'learner-notes')
        self.assertEqual(classify_source('Kế toán chi phí/tmp/x.pdf')['partition'], 'excluded')
        self.assertEqual(classify_source('Kế toán chi phí/_nguon/KTCP-C1-CD1.1.pdf')['source_role'], 'lecture_note')

    def test_bad_paths_and_chains(self):
        for path in ('../x', '/x', 'C:/x', '_learning_system/x'):
            with self.assertRaises(ValueError):
                safe_relative(path)
        with self.assertRaises(ValueError):
            active_records([self.row, {**self.row, 'source_id': 'src-0002'}])
        with self.assertRaises(ValueError):
            active_records([{**self.row, 'supersedes': 'src-9999'}])

    def test_same_size_limit_explicit(self):
        changed = {**self.row, 'sha256': 'different'}
        self.assertEqual(compare([changed], [self.row])['CHANGED'], [])

    def test_real_unit_script_ram_ingestion(self):
        inv = json.loads((SYSTEM / 'inventory/files.json').read_text(encoding='utf-8'))
        source = next(r for r in active_records(inv) if r['course_id'] == 'ke-toan-chi-phi' and '/_nguon/' in r['relative_path'] and r['extension'] == '.pdf')
        payload = (SOURCE_ROOT / source['relative_path']).read_bytes()
        self.assertEqual(digest(payload), source['sha256'])
        new_path = str(Path(source['relative_path']).with_name('RAM_SIM_' + source['filename'])).replace('\\', '/')
        mirror = {new_path: payload}
        delta = compare([{'relative_path': new_path, 'size_bytes': len(payload)}], [])
        self.assertEqual(len(delta['NEW']), 1)
        guard(delta)
        reader, plumber = extractor.PdfReader, extractor.pdfplumber.open
        # Only replace file transport; production extractor and both PDF parsers run.
        with patch.object(extractor, 'PdfReader', side_effect=lambda _: reader(io.BytesIO(mirror[new_path]))), \
             patch.object(extractor.pdfplumber, 'open', side_effect=lambda _: plumber(io.BytesIO(mirror[new_path]))):
            extracted = extractor.extract_pdf(Path(new_path))
        self.assertTrue(extracted['ok'], extracted.get('error'))
        self.assertEqual(extracted['page_count'], len(extracted['pages']))
        entry = {**delta['NEW'][0], 'sha256': digest(payload), **classify_source(new_path, extracted['pages'][0]['text'])}
        updated = append_records(inv, [entry])
        sid = updated[-1]['source_id']
        chunks = [{'chunk_id': f'chk-{sid}-{i:04d}', 'source_id': sid, 'course_id': entry['course_id'],
                   'text': u['text'], 'provenance': {'source_sha256': digest(payload)}}
                  for i, u in enumerate(pages_to_units(extracted['pages']), 1) if len(u['text']) >= 80]
        self.assertTrue(chunks)
        MemoryPath.files['chunks'] = ''.join(json.dumps(c, ensure_ascii=False) + '\n' for c in chunks)
        with patch.object(lexical, 'Path', MemoryPath):
            built = lexical.build_index('chunks', 'index', {'index_version': '3.0.0'})
            index = lexical.Index('chunks', 'index')
            scores = index.bm25(tokenize(chunks[0]['text'][:100]))
            self.assertGreater(float(scores.max()), 0)
            self.assertIn(sid, {c['source_id'] for c in index.chunks})
            self.assertEqual(built['meta']['source_hashes'], [digest(payload)])
        self.assertFalse(compare([{'relative_path': new_path, 'size_bytes': len(payload)}], [updated[-1]])['NEW'])
        count = len(chunks)
        mirror.clear()
        MemoryPath.files.clear()
        self.assertFalse(mirror)
        self.assertFalse(MemoryPath.files)
        SIMULATION.update(source_id=source['source_id'], source_sha256=digest(payload), pages=extracted['page_count'],
                          chunks=count, simulated_new_detected=True, indexed_and_retrievable=True,
                          removed_from_ram=True, source_files_written=0,
                          limit='RAM transport test; not a disk-publication or concurrent-reader acceptance test')


SIMULATION = {}
if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(RefreshTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    output = {'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
              'all_pass': result.wasSuccessful(), 'simulation': SIMULATION}
    (SYSTEM / 'reports/v3/refresh_selftest.json').write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    raise SystemExit(0 if result.wasSuccessful() else 1)
