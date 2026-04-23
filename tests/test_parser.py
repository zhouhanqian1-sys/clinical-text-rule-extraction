from __future__ import annotations

import pytest

from clinical_text_parser.parser import ClinicalTextParser, parse_clinical_text


def test_extracts_symptom_severity_duration_and_association() -> None:
    result = parse_clinical_text(
        "Patient has had severe chest pain for 2 days with shortness of breath."
    )

    chest_pain = next(
        mention for mention in result.mentions if mention.symptom == "chest pain"
    )
    shortness_of_breath = next(
        mention
        for mention in result.mentions
        if mention.symptom == "shortness of breath"
    )

    assert chest_pain.severity == "severe"
    assert chest_pain.duration == "2 days"
    assert chest_pain.body_location == "chest"
    assert chest_pain.negated is False
    assert "shortness of breath" in chest_pain.associated_symptoms
    assert "chest pain" in shortness_of_breath.associated_symptoms
    assert shortness_of_breath.duration is None


def test_extracts_multiple_symptoms_in_one_sentence() -> None:
    result = parse_clinical_text("Patient reports fever and cough.")

    assert [mention.symptom for mention in result.mentions] == ["fever", "cough"]
    assert result.mentions[0].associated_symptoms == ["cough"]
    assert result.mentions[1].associated_symptoms == ["fever"]


def test_detects_negated_symptoms() -> None:
    result = parse_clinical_text("Patient denies fever or cough.")

    assert len(result.mentions) == 2
    assert all(mention.negated for mention in result.mentions)


def test_handles_case_and_spelling_variation() -> None:
    result = parse_clinical_text("SEVERE shortness-of-breath x 2 DAYS and head ache.")

    shortness_of_breath = next(
        mention
        for mention in result.mentions
        if mention.symptom == "shortness of breath"
    )
    headache = next(
        mention for mention in result.mentions if mention.symptom == "headache"
    )

    assert shortness_of_breath.severity == "severe"
    assert shortness_of_breath.duration == "2 days"
    assert headache.body_location == "head"


def test_empty_input_returns_no_mentions() -> None:
    parser = ClinicalTextParser()
    result = parser.parse("   ")

    assert result.normalized_text == ""
    assert result.mentions == []


def test_non_string_input_raises_type_error() -> None:
    parser = ClinicalTextParser()

    with pytest.raises(TypeError):
        parser.parse(None)  # type: ignore[arg-type]


def test_negation_with_contrast_scope() -> None:
    result = parse_clinical_text("Patient denies fever but has cough.")
    fever = next(mention for mention in result.mentions if mention.symptom == "fever")
    cough = next(mention for mention in result.mentions if mention.symptom == "cough")

    assert fever.negated is True
    assert cough.negated is False


def test_extracts_leading_duration_history_pattern() -> None:
    result = parse_clinical_text("Patient has 1-week history of cough.")
    cough = next(mention for mention in result.mentions if mention.symptom == "cough")

    assert cough.duration == "1 week"


def test_extracts_synonym_mentions() -> None:
    result = parse_clinical_text("Dyspnea with emesis and lightheadedness.")
    symptoms = [mention.symptom for mention in result.mentions]

    assert symptoms == ["shortness of breath", "vomiting", "dizziness"]
