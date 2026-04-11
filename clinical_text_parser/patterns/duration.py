"""Duration-related patterns."""

from __future__ import annotations

import re

NUMBER_PATTERN = r"(?:\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten)"
TIME_UNIT_PATTERN = r"(?:hour|hours|day|days|week|weeks|month|months|year|years)"

TRAILING_DURATION_PATTERNS: tuple[str, ...] = (
    rf"\bfor (?P<duration>{NUMBER_PATTERN}\s+{TIME_UNIT_PATTERN})\b",
    rf"\bx\s*(?P<duration>{NUMBER_PATTERN}\s+{TIME_UNIT_PATTERN})\b",
)

LEADING_DURATION_PATTERNS: tuple[str, ...] = (
    rf"\b(?P<duration>{NUMBER_PATTERN}[ -]{TIME_UNIT_PATTERN})\s+(?:history|hx)\b",
)


def normalize_duration(value: str) -> str:
    normalized = value.replace("-", " ")
    return re.sub(r"\s+", " ", normalized).strip()
