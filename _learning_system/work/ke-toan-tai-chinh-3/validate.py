# Runs scripts/v3_validate_concepts.py unchanged, adding the missing W6b prefix in memory only
# (PREFIX lacks ke-toan-tai-chinh-3; adding it to the shared script is a Pha C task).
import sys
from pathlib import Path
SYS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SYS))
import scripts.v3_validate_concepts as V
V.PREFIX.setdefault("ke-toan-tai-chinh-3", "kttc3")
sys.argv = ["v3_validate_concepts.py", "--course", "ke-toan-tai-chinh-3"]
V.main()
