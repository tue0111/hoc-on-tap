# -*- coding: utf-8 -*-
"""Run scripts/v3_validate_concepts.py for ke-toan-thue-1 without editing the shared script:
its PREFIX map has no entry for the W6b courses yet (Pha C), so add 'thue1' in memory only."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
import v3_validate_concepts as V
V.PREFIX["ke-toan-thue-1"] = "thue1"
sys.argv = ["v3_validate_concepts.py", "--course", "ke-toan-thue-1"]
V.main()
