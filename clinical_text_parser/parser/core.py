"""Core rule-based parser for short clinical text."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass

from clinical_text_parser.models import ParsedClinicalText, SymptomMention
from clinical_text_parser.parser.normalizer import normalize_text
from clinical_text_parser.patterns import (
    BODY_LOCATION_PATTERNS,
    CONTRAST_CUES,
    LEADING_DURATION_PATTERNS,
    NEGATION_CUES,
    NEGATION_LOOKBACK_CHARS,
    SEVERITY_NORMALIZATION,
    SYMPTOM_PATTERNS,
    TRAILING_DURATION_PATTERNS,
    normalize_duration,
)

# Compile a regex to detect severity terms such as "mild"
SEVERITY_REGEX = re.compile(
    r"\b(" + "|".join(re.escape(term) for term in SEVERITY_NORMALIZATION) + r")\b",
    flags=re.IGNORECASE,
)

# Compile regex patterns for durations that appear after symptoms
TRAILING_DURATION_REGEXES = [
    re.compile(pattern, flags=re.IGNORECASE) for pattern in TRAILING_DURATION_PATTERNS
]

# Compile regex patterns for durations that appear before symptoms
LEADING_DURATION_REGEXES = [
    re.compile(pattern, flags=re.IGNORECASE) for pattern in LEADING_DURATION_PATTERNS
]

# Compile a regex to detect negation cues such as "no"
NEGATION_REGEX = re.compile(
    r"\b(" + "|".join(re.escape(cue) for cue in NEGATION_CUES) + r")\b",
    flags=re.IGNORECASE,
)

# Compile a regex to detect contrast words such as "but"
CONTRAST_REGEX = re.compile(
    r"\b(" + "|".join(re.escape(cue) for cue in CONTRAST_CUES) + r")\b",
    flags=re.IGNORECASE,
)
# Compile regex patterns for body location terms
BODY_LOCATION_REGEXES = [
    (name, re.compile(pattern, flags=re.IGNORECASE))
    for name, pattern in BODY_LOCATION_PATTERNS
]

# Compile regex patterns for symptom mentions
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

    # Parse clinical text and return a structured result
    def parse(self, text: str) -> ParsedClinicalText:
        if not isinstance(text, str):
            raise TypeError("ClinicalTextParser.parse expects a string input.")
        # Normalize the input text
        normalized = normalize_text(text)
        if not normalized:
            return ParsedClinicalText(text=text, normalized_text="", mentions=[])
        
        # Split the text into sentences and find symptom matches
        sentences = _split_sentences(normalized)
        matches = self._find_symptom_matches(normalized)

        # Store symptom mentions together with their sentence index
        mention_records: list[tuple[SymptomMention, int]] = []
        for match in matches:
            # Locate the sentence containing the symptom match
            sentence_index, sentence, sentence_start = _locate_sentence(
                match.start, sentences
            )

            # Calculate the position of the match relative to the start of the sentence
            relative_start = match.start - sentence_start
            relative_end = match.end - sentence_start
            
            # Extract attributes and create a SymptomMention object
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

        # Extract only the mention objects
        mentions = [mention for mention, _ in mention_records]
        return ParsedClinicalText(
            text=text, normalized_text=normalized, mentions=mentions
        )

    # Find all symptom matches in the input text
    def _find_symptom_matches(self, text: str) -> list[_MatchedSymptom]:
        raw_matches: list[_MatchedSymptom] = []
        for symptom_pattern, compiled_regex in SYMPTOM_REGEXES:
            # Search for all matches of the current symptom pattern in the text
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
        # Store non-overlapping matches only
        deduplicated: list[_MatchedSymptom] = []
        for candidate in raw_matches:
            if any(_overlaps(candidate, existing) for existing in deduplicated):
                continue
            deduplicated.append(candidate)
        return sorted(deduplicated, key=lambda item: item.start)

    # Extract severity information near a symptom mention
    def _extract_severity(self, sentence: str, start: int, end: int) -> str | None:
        before_window = sentence[max(0, start - 24) : start]
        after_window = sentence[end : min(len(sentence), end + 24)]

        for window, use_last in ((before_window, True), (after_window, False)):
            matches = list(SEVERITY_REGEX.finditer(window))
            if not matches:
                continue

            # Use the closest severity match to the symptom mention
            match = matches[-1] if use_last else matches[0]
            return SEVERITY_NORMALIZATION[match.group(1).lower()]
        return None
    
    # Extract duration information near a symptom mention
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

    # Extract body location information near a symptom mention
    def _extract_body_location(
        self,
        sentence: str,
        start: int,
        end: int,
        default_location: str | None,
    ) -> str | None:
        if default_location:
            return default_location

        window_start = max(0, start - 15)
        window_end = min(len(sentence), end + 15)
        context_window = sentence[window_start:window_end]

        for location, pattern in BODY_LOCATION_REGEXES:
            if pattern.search(context_window):
                return location
        return None
    
    # Determine if a symptom mention is negated
    def _is_negated(self, sentence: str, start: int) -> bool:
        left_context = sentence[max(0, start - NEGATION_LOOKBACK_CHARS) : start]
        cue_matches = list(NEGATION_REGEX.finditer(left_context))

        if not cue_matches:
            return False

        last_cue = cue_matches[-1]
        tail_after_last_cue = left_context[last_cue.end() :]

        if CONTRAST_REGEX.search(tail_after_last_cue):
            return False

        return True

    # Attach associated symptoms that appear in the same sentence
    def _attach_associations(
        self,
        mention_records: list[tuple[SymptomMention, int]],
    ) -> None:
        grouped_mentions: dict[int, list[SymptomMention]] = defaultdict(list)
        for mention, sentence_index in mention_records:
            grouped_mentions[sentence_index].append(mention)

        for mentions in grouped_mentions.values():
            symptoms_in_sentence = [mention.symptom for mention in mentions]
            unique_symptoms = set(symptoms_in_sentence)

            if len(unique_symptoms) < 2:
                continue
            for mention in mentions:
                other_symptoms = [
                    symptom for symptom in unique_symptoms
                    if symptom != mention.symptom
                ]
                mention.associated_symptoms = other_symptoms

# Public function to parse clinical text using the ClinicalTextParser class
def parse_clinical_text(text: str) -> ParsedClinicalText:
    return ClinicalTextParser().parse(text)


# Helper functions for sentence splitting, locating sentences, and checking overlaps
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

# Trim leading and trailing spaces and commas from a text chunk
def _trim_chunk(text: str, start: int, end: int) -> tuple[int, int]:
    while start < end and text[start] in {" ", ","}:
        start += 1
    while end > start and text[end - 1] in {" ", ","}:
        end -= 1
    return start, end

# Locate the sentence containing a given character span
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

# Check if two symptom matches overlap in their character spans
def _overlaps(left: _MatchedSymptom, right: _MatchedSymptom) -> bool:
    return left.start < right.end and right.start < left.end
