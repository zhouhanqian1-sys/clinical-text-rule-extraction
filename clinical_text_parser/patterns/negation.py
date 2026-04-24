"""Negation cues used by the parser."""

NEGATION_CUES: tuple[str, ...] = (
    "no",
    "denies",
    "denied",
    "without",
    "negative for",
    "free of",
)

CONTRAST_CUES: tuple[str, ...] = (
    "but",
    "however",
    "except",
)

AFFIRMATIVE_CLAUSE_BOUNDARY_PATTERNS: tuple[str, ...] = (
    r"\b(?:and|,)\s+(?:has|have|had)\b",
    r"\b(?:and|,)\s+(?:report|reports|reported)\b",
    r"\b(?:and|,)\s+(?:note|notes|noted)\b",
    r"\b(?:and|,)\s+(?:present|presents|presented)\b",
    r"\b(?:and|,)\s+(?:complain|complains|complained)\b",
)

NEGATION_LOOKBACK_CHARS = 45
