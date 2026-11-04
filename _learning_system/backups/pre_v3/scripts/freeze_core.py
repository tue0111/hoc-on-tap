# -*- coding: utf-8 -*-
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"D:\Hoc\_learning_system")))

from study.freeze import write_manifest
from study.integrity import BLOCK


def main():
    man = write_manifest()
    print(json.dumps({"status": man["source_integrity"]["status"], "checked": man["source_integrity"]["checked"], "path": str(Path(r"D:\Hoc\_learning_system\pilot\core_freeze_manifest.json"))}, indent=2))
    if man["source_integrity"]["status"] == BLOCK:
        sys.exit(2)


if __name__ == "__main__":
    main()
