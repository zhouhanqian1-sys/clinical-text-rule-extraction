"""Body location lexicon used by the parser."""

BODY_LOCATION_PATTERNS: tuple[tuple[str, str], ...] = (
    ("chest", r"\bchest\b"),
    ("head", r"\bhead\b"),
    ("abdomen", r"\b(?:abdomen|abdominal|stomach)\b"),
    ("back", r"\bback\b"),
    ("throat", r"\bthroat\b"),
    ("leg", r"\bleg\b"),
    ("arm", r"\barm\b"),
)
