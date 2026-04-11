# Clinical Text Rule Extraction

A small Python library for extracting structured symptom information from short clinical text without using APIs or LLMs.

## Why this project

This repository is designed as a course-friendly software engineering project:

- clear input and output
- reusable parsing logic independent from the CLI
- easy to test
- no external API keys
- clinically meaningful while still being a real library project

## Features

- extract symptom mentions
- extract severity
- extract duration
- extract body location
- detect simple negation
- emit consistent JSON output
- provide both Python and CLI interfaces

## Example

Input:

```text
Patient has had severe chest pain for 2 days with shortness of breath.
```

Output:

```json
{
  "text": "Patient has had severe chest pain for 2 days with shortness of breath.",
  "normalized_text": "patient has had severe chest pain for 2 days with shortness of breath.",
  "mentions": [
    {
      "symptom": "chest pain",
      "matched_text": "chest pain",
      "severity": "severe",
      "duration": "2 days",
      "body_location": "chest",
      "negated": false,
      "associated_symptoms": [
        "shortness of breath"
      ],
      "evidence": "patient has had severe chest pain for 2 days with shortness of breath"
    },
    {
      "symptom": "shortness of breath",
      "matched_text": "shortness of breath",
      "severity": null,
      "duration": null,
      "body_location": null,
      "negated": false,
      "associated_symptoms": [
        "chest pain"
      ],
      "evidence": "patient has had severe chest pain for 2 days with shortness of breath"
    }
  ]
}
```

## Project Structure

```text
clinical-text-rule-extraction/
├── clinical_text_parser/
│   ├── cli/
│   ├── io/
│   ├── models/
│   ├── parser/
│   └── patterns/
├── tests/
├── pyproject.toml
└── README.md
```

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Python Usage

```python
from clinical_text_parser import ClinicalTextParser

parser = ClinicalTextParser()
result = parser.parse("Patient denies fever but reports mild cough for 3 days.")

print(result.to_dict())
```

## CLI Usage

Parse a single string:

```bash
clinical-text-parser --text "Patient has severe chest pain for 2 days."
```

Parse a text file with one input per line:

```bash
clinical-text-parser --input-file sample_notes.txt --output-file results.json
```

## Testing

```bash
python -m pytest
```

## Current Scope

This is intentionally a lightweight rule-based baseline. It works best on short symptom-focused text snippets and can be extended with:

- richer symptom lexicons
- more robust scope handling for negation
- section-aware parsing
- better attachment rules for modifiers in multi-symptom sentences
- optional FHIR-style schema output
