"""Normalization helpers for short clinical text."""

from __future__ import annotations

import re


def normalize_text(text: str) -> str:
    normalized = text.strip().lower()
    normalized = normalized.replace("/", " ")
    normalized = re.sub(r"-+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized
