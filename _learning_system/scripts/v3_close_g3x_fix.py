"""Record verified G3x repair without changing frozen evaluation history."""
import hashlib
import json
import sys
from pathlib import Path
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from retrieval.config import SYSTEM
from scripts.v3_debug_g3x import TARGETS

if __name__ == '__main__':
    regression = Path(sys.argv[1])
    assert (SYSTEM / regression / 'diff.txt').read_text().strip() == 'IDENTICAL'
    frozen = json.loads((SYSTEM / 'evals/v3/FROZEN.json').read_text(encoding='utf-8'))
    for entry in frozen.values():
        assert hashlib.sha256((SYSTEM / entry['file']).read_bytes()).hexdigest() == entry['sha256']
    for cid in TARGETS + ['learner-notes']:
        result = json.loads((SYSTEM / f'reports/v3/{cid}_eval_g3x_fixed.json').read_text(encoding='utf-8'))
        assert result['all_pass'], cid
    path = SYSTEM / 'autopilot/v3_progress.yaml'
    progress = yaml.safe_load(path.read_text(encoding='utf-8'))
    progress['current_step'] = 'G3x repaired and verified; next Wave 4'
    progress['steps']['G3x.fix'] = dict(status='done', at='2026-10-11', note=f'User authorized debug/fix; seven course gates pass, learner-notes pass, all frozen hashes unchanged; regression {regression}')
    for gate in ['G1','G2b','G3a','G3f']:
        progress['gates'][gate].update(status='pass', tier='retrieval', resolution_report='reports/v3/G3x_FIX.md')
    progress['gates']['G3x'].update(status='pass', report='reports/v3/G3x_FIX.md', passed=TARGETS, failed_to_catalog=[], previous_report='reports/v3/G3x.md')
    for escalation in progress['escalations']:
        if escalation['step'].startswith('G3x/'):
            escalation['resolution'] = 'Resolved by authorized engine/routing fix; reports/v3/G3x_FIX.md'
    path.write_text(yaml.safe_dump(progress, allow_unicode=True, sort_keys=False), encoding='utf-8')
    print('Verified frozen hashes, all repaired gates, regression; progress updated')
