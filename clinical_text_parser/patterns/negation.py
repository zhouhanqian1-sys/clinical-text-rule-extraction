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

NEGATION_LOOKBACK_CHARS = 45
