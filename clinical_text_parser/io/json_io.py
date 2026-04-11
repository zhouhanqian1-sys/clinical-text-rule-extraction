"""I/O helpers for the clinical text parser."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_text_lines(path: str | Path) -> list[str]:
    file_path = Path(path)
    return [
        line.strip()
        for line in file_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def dump_json(payload: Any, path: str | Path | None = None, indent: int = 2) -> str:
    rendered = json.dumps(payload, indent=indent, ensure_ascii=False)
    if path is not None:
        Path(path).write_text(f"{rendered}\n", encoding="utf-8")
    return rendered
