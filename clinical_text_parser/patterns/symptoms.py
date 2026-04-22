"""Symptom lexicon for short clinical text extraction."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SymptomPattern:
    canonical: str
    pattern: str
    body_location: str | None = None


SYMPTOM_PATTERNS: tuple[SymptomPattern, ...] = (
    SymptomPattern("chest pain", r"\bchest pain\b", "chest"),
    SymptomPattern(
        "shortness of breath",
        (
            r"\b(?:shortness of breath|shortness[- ]of[- ]breath|"
            r"sob|dyspnea)\b"
        ),
    ),
    SymptomPattern("fever", r"\bfever\b"),
    SymptomPattern("cough", r"\bcough(?:ing)?\b"),
    SymptomPattern("headache", r"\b(?:headache|head ache)\b", "head"),
    SymptomPattern("nausea", r"\bnausea\b"),
    SymptomPattern("vomiting", r"\b(?:vomiting|emesis)\b"),
    SymptomPattern(
        "abdominal pain", r"\b(?:abdominal|abdomen|stomach) pain\b", "abdomen"
    ),
    SymptomPattern("back pain", r"\bback pain\b", "back"),
    SymptomPattern("dizziness", r"\b(?:dizziness|lightheadedness)\b"),
    SymptomPattern("fatigue", r"\b(?:fatigue|tiredness)\b"),
    SymptomPattern("diarrhea", r"\bdiarrhea\b"),
    SymptomPattern("sore throat", r"\bsore throat\b", "throat"),
    SymptomPattern("palpitations", r"\bpalpitations?\b"),
    SymptomPattern("wheezing", r"\bwheez(?:e|ing)\b"),
)
