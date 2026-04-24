"""Reusable lexicons and regex patterns for rule-based extraction."""

from clinical_text_parser.patterns.body_locations import BODY_LOCATION_PATTERNS
from clinical_text_parser.patterns.duration import (
    LEADING_DURATION_PATTERNS,
    TRAILING_DURATION_PATTERNS,
    normalize_duration,
)
from clinical_text_parser.patterns.negation import (
    CONTRAST_CUES,
    NEGATION_CUES,
    NEGATION_LOOKBACK_CHARS,
)
from clinical_text_parser.patterns.severity import SEVERITY_NORMALIZATION
from clinical_text_parser.patterns.symptoms import SYMPTOM_PATTERNS, SymptomPattern

__all__ = [
    "BODY_LOCATION_PATTERNS",
    "LEADING_DURATION_PATTERNS",
    "NEGATION_CUES",
    "CONTRAST_CUES",
    "NEGATION_LOOKBACK_CHARS",
    "SEVERITY_NORMALIZATION",
    "SYMPTOM_PATTERNS",
    "SymptomPattern",
    "TRAILING_DURATION_PATTERNS",
    "normalize_duration",
]
