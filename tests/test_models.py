from clinical_text_parser.models import ParsedClinicalText, SymptomMention


def test_symptom_mention_to_dict() -> None:
    mention = SymptomMention(
        symptom="chest pain",
        matched_text="chest pain",
        severity="severe",
        duration="2 days",
        body_location="chest",
        negated=False,
        associated_symptoms=["shortness of breath"],
        evidence="patient has had severe chest pain for 2 days",
    )

    assert mention.to_dict() == {
        "symptom": "chest pain",
        "matched_text": "chest pain",
        "severity": "severe",
        "duration": "2 days",
        "body_location": "chest",
        "negated": False,
        "associated_symptoms": ["shortness of breath"],
        "evidence": "patient has had severe chest pain for 2 days",
    }


def test_parsed_clinical_text_to_dict() -> None:
    result = ParsedClinicalText(
        text="Patient has chest pain.",
        normalized_text="patient has chest pain.",
        mentions=[
            SymptomMention(
                symptom="chest pain",
                matched_text="chest pain",
                evidence="patient has chest pain",
            )
        ],
    )

    assert result.to_dict() == {
        "text": "Patient has chest pain.",
        "normalized_text": "patient has chest pain.",
        "mentions": [
            {
                "symptom": "chest pain",
                "matched_text": "chest pain",
                "severity": None,
                "duration": None,
                "body_location": None,
                "negated": False,
                "associated_symptoms": [],
                "evidence": "patient has chest pain",
            }
        ],
    }


def test_parsed_clinical_text_empty_mentions() -> None:
    result = ParsedClinicalText(
        text="",
        normalized_text="",
    )

    assert result.to_dict() == {
        "text": "",
        "normalized_text": "",
        "mentions": [],
    }
