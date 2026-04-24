"""Data models for structured clinical text extraction output."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SymptomMention:
    """Structured representation of a single symptom mention."""

    symptom: str
    matched_text: str
    severity: str | None = None
    duration: str | None = None
    body_location: str | None = None
    negated: bool = False
    associated_symptoms: list[str] = field(default_factory=list)
    evidence: str = ""

    def to_dict(self) -> dict[str, object]:
        """Convert the symptom mention to a JSON-serializable dictionary."""
        return {
            "symptom": self.symptom,
            "matched_text": self.matched_text,
            "severity": self.severity,
            "duration": self.duration,
            "body_location": self.body_location,
            "negated": self.negated,
            "associated_symptoms": self.associated_symptoms,
            "evidence": self.evidence,
        }


@dataclass
class ParsedClinicalText:
    """Structured parser output for a full clinical text snippet."""

    text: str
    normalized_text: str
    mentions: list[SymptomMention] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        """Convert the parsed result to a JSON-serializable dictionary."""
        return {
            "text": self.text,
            "normalized_text": self.normalized_text,
            "mentions": [mention.to_dict() for mention in self.mentions],
        }
