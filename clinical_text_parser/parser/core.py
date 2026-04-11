"""Core rule-based parser for short clinical text."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import re

from clinical_text_parser.models import ParsedClinicalText, SymptomMention
from clinical_text_parser.patterns import (
    BODY_LOCATION_PATTERNS,
    LEADING_DURATION_PATTERNS,
    NEGATION_CUES,
    SEVERITY_NORMALIZATION,
    SYMPTOM_PATTERNS,
    TRAILING_DURATION_PATTERNS,
    normalize_duration,
)
from clinical_text_parser.parser.normalizer import normalize_text


SEVERITY_REGEX = re.compile(
    r"\b(" + "|".join(re.escape(term) for term in SEVERITY_NORMALIZATION) + r")\b",
    flags=re.IGNORECASE,
)
TRAILING_DURATION_REGEXES = [
    re.compile(pattern, flags=re.IGNORECASE) for pattern in TRAILING_DURATION_PATTERNS
]
LEADING_DURATION_REGEXES = [
    re.compile(pattern, flags=re.IGNORECASE) for pattern in LEADING_DURATION_PATTERNS
]
NEGATION_REGEX = re.compile(
    r"\b(" + "|".join(re.escape(cue) for cue in NEGATION_CUES) + r")\b",
    flags=re.IGNORECASE,
)
CONTRAST_REGEX = re.compile(r"\b(?:but|however|except)\b", flags=re.IGNORECASE)
BODY_LOCATION_REGEXES = [
    (name, re.compile(pattern, flags=re.IGNORECASE))
    for name, pattern in BODY_LOCATION_PATTERNS
]
SYMPTOM_REGEXES = [
    (pattern, re.compile(pattern.pattern, flags=re.IGNORECASE))
    for pattern in SYMPTOM_PATTERNS
]


@dataclass(frozen=True)
class _MatchedSymptom:
    canonical: str
    matched_text: str
    start: int
    end: int
    default_body_location: str | None = None


class ClinicalTextParser:
    """Rule-based parser for symptom-focused clinical text."""

    def parse(self, text: str) -> ParsedClinicalText:
        if not isinstance(text, str):
            raise TypeError("ClinicalTextParser.parse expects a string input.")

        normalized = normalize_text(text)
        if not normalized:
            return ParsedClinicalText(text=text, normalized_text="", mentions=[])

        sentences = _split_sentences(normalized)
        matches = self._find_symptom_matches(normalized)

        mention_records: list[tuple[SymptomMention, int]] = []
        for match in matches:
            sentence_index, sentence, sentence_start = _locate_sentence(match.start, sentences)
            relative_start = match.start - sentence_start
            relative_end = match.end - sentence_start

            mention = SymptomMention(
                symptom=match.canonical,
                matched_text=match.matched_text,
                severity=self._extract_severity(sentence, relative_start, relative_end),
                duration=self._extract_duration(sentence, relative_start, relative_end),
                body_location=self._extract_body_location(
                    sentence,
                    relative_start,
                    relative_end,
                    default_location=match.default_body_location,
                ),
                negated=self._is_negated(sentence, relative_start),
                evidence=sentence.strip(),
            )
            mention_records.append((mention, sentence_index))

        self._attach_associations(mention_records)
        mentions = [mention for mention, _ in mention_records]
        return ParsedClinicalText(text=text, normalized_text=normalized, mentions=mentions)

    def _find_symptom_matches(self, text: str) -> list[_MatchedSymptom]:
        raw_matches: list[_MatchedSymptom] = []
        for symptom_pattern, compiled_regex in SYMPTOM_REGEXES:
            for match in compiled_regex.finditer(text):
                raw_matches.append(
                    _MatchedSymptom(
                        canonical=symptom_pattern.canonical,
                        matched_text=match.group(0),
                        start=match.start(),
                        end=match.end(),
                        default_body_location=symptom_pattern.body_location,
                    )
                )

        raw_matches.sort(key=lambda item: (item.start, -(item.end - item.start)))
        deduplicated: list[_MatchedSymptom] = []
        for candidate in raw_matches:
            if any(_overlaps(candidate, existing) for existing in deduplicated):
                continue
            deduplicated.append(candidate)
        return sorted(deduplicated, key=lambda item: item.start)

    def _extract_severity(self, sentence: str, start: int, end: int) -> str | None:
        before_window = sentence[max(0, start - 24) : start]
        after_window = sentence[end : min(len(sentence), end + 24)]

        for window, use_last in ((before_window, True), (after_window, False)):
            matches = list(SEVERITY_REGEX.finditer(window))
            if not matches:
                continue
            match = matches[-1] if use_last else matches[0]
            return SEVERITY_NORMALIZATION[match.group(1).lower()]
        return None

    def _extract_duration(self, sentence: str, start: int, end: int) -> str | None:
        trailing_window = sentence[end : min(len(sentence), end + 40)]
        leading_window = sentence[max(0, start - 30) : start]

        for pattern in TRAILING_DURATION_REGEXES:
            match = pattern.search(trailing_window)
            if match:
                return normalize_duration(match.group("duration").lower())

        for pattern in LEADING_DURATION_REGEXES:
            match = pattern.search(leading_window)
            if match:
                return normalize_duration(match.group("duration").lower())
        return None

    def _extract_body_location(
        self,
        sentence: str,
        start: int,
        end: int,
        default_location: str | None,
    ) -> str | None:
        if default_location:
            return default_location

        context_window = sentence[max(0, start - 15) : min(len(sentence), end + 15)]
        for location, pattern in BODY_LOCATION_REGEXES:
            if pattern.search(context_window):
                return location
        return None

    def _is_negated(self, sentence: str, start: int) -> bool:
        left_context = sentence[max(0, start - 45) : start]
        cue_matches = list(NEGATION_REGEX.finditer(left_context))
        if not cue_matches:
            return False

        tail_after_last_cue = left_context[cue_matches[-1].end() :]
        return CONTRAST_REGEX.search(tail_after_last_cue) is None

    def _attach_associations(
        self,
        mention_records: list[tuple[SymptomMention, int]],
    ) -> None:
        grouped_mentions: dict[int, list[SymptomMention]] = defaultdict(list)
        for mention, sentence_index in mention_records:
            grouped_mentions[sentence_index].append(mention)

        for mentions in grouped_mentions.values():
            unique_symptoms = list(dict.fromkeys(mention.symptom for mention in mentions))
            if len(unique_symptoms) < 2:
                continue
            for mention in mentions:
                mention.associated_symptoms = [
                    symptom for symptom in unique_symptoms if symptom != mention.symptom
                ]


def parse_clinical_text(text: str) -> ParsedClinicalText:
    return ClinicalTextParser().parse(text)


def _split_sentences(text: str) -> list[tuple[str, int, int]]:
    sentences: list[tuple[str, int, int]] = []
    start = 0

    for match in re.finditer(r"[.!?;]+", text):
        chunk_start, chunk_end = _trim_chunk(text, start, match.start())
        if chunk_start < chunk_end:
            sentences.append((text[chunk_start:chunk_end], chunk_start, chunk_end))
        start = match.end()

    chunk_start, chunk_end = _trim_chunk(text, start, len(text))
    if chunk_start < chunk_end:
        sentences.append((text[chunk_start:chunk_end], chunk_start, chunk_end))

    return sentences or [(text, 0, len(text))]


def _trim_chunk(text: str, start: int, end: int) -> tuple[int, int]:
    while start < end and text[start] in {" ", ","}:
        start += 1
    while end > start and text[end - 1] in {" ", ","}:
        end -= 1
    return start, end


def _locate_sentence(
    span_start: int,
    sentences: list[tuple[str, int, int]],
) -> tuple[int, str, int]:
    for index, (sentence, sentence_start, sentence_end) in enumerate(sentences):
        if sentence_start <= span_start < sentence_end:
            return index, sentence, sentence_start
    last_index = len(sentences) - 1
    last_sentence, last_start, _ = sentences[last_index]
    return last_index, last_sentence, last_start


def _overlaps(left: _MatchedSymptom, right: _MatchedSymptom) -> bool:
    return left.start < right.end and right.start < left.end
