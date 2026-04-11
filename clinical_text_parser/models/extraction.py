"""Structured result models for extracted clinical text information."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class SymptomMention:
    symptom: str
    matched_text: str
    severity: str | None = None
    duration: str | None = None
    body_location: str | None = None
    negated: bool = False
    associated_symptoms: list[str] = field(default_factory=list)
    evidence: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ParsedClinicalText:
    text: str
    normalized_text: str
    mentions: list[SymptomMention] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "normalized_text": self.normalized_text,
            "mentions": [mention.to_dict() for mention in self.mentions],
        }
