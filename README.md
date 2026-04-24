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

## Software Architecture

This project is designed as a small, reusable Python library with a thin command-line interface.

The architecture separates the core business logic from the user interface:

- the **library layer** performs rule-based clinical text parsing
- the **CLI layer** only handles user input, file arguments, and output formatting

This design makes the project easier to test, reuse, and extend.

### Main Components

- `clinical_text_parser.patterns`  
  Contains symptom vocabularies, severity terms, duration expressions, body-location terms, and negation trigger patterns.

- `clinical_text_parser.parser`  
  Implements the core extraction pipeline. This module identifies symptom mentions and attaches related attributes such as severity, duration, body location, and negation status.

- `clinical_text_parser.models`  
  Defines the structured result objects returned by the parser, such as mention-level outputs and full parse results.

- `clinical_text_parser.io`  
  Handles input/output helpers, including reading text from files and writing structured JSON results.

- `clinical_text_parser.cli`  
  Provides the command-line entry point. This layer calls the library but does not implement parsing logic itself.

### Data Flow

1. Raw clinical text is provided through the Python API or CLI.
2. The text is normalized for consistent matching.
3. Rule-based patterns are used to identify symptom mentions.
4. Additional rules attach severity, duration, body location, and negation information.
5. The parser returns structured result objects.
6. Results can be converted to dictionaries or JSON for downstream use.

### Design Rationale

This architecture was chosen to support:

- **reusability**: the parser can be imported as a normal Python library
- **testability**: core parsing logic can be tested independently from the CLI
- **maintainability**: patterns, parser logic, data models, and interface code are kept separate
- **extensibility**: new rules or output formats can be added without changing the overall structure

## Project Structure

```text
clinical-text-rule-extraction-main/
├── clinical_text_parser/
│   ├── __init__.py
│   ├── cli/           # Command-line interface
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   └── main.py
│   ├── io/            # Input and output helpers
│   │   ├── __init__.py
│   │   └── json_io.py
│   ├── models/        # Structured result models
│   │   ├── __init__.py
│   │   └── extraction.py
│   ├── parser/        # Core rule-based parsing logic
│   │   ├── __init__.py
│   │   ├── core.py
│   │   └── normalizer.py
│   └── patterns/      # Symptom and attribute rule patterns
│       ├── __init__.py
│       ├── body_locations.py
│       ├── duration.py
│       ├── negation.py
│       ├── severity.py
│       └── symptoms.py
├── tests/            # Automated tests
│   ├── test_cli.py
│   ├── test_models.py
│   └── test_parser.py
├── AI_USAGE.md        # Documentation of AI tool usage
├── LICENSE            # Project license
├── pyproject.toml     # Project configuration
├── README.md          # Project documentation
├── results.json       # Example output file
└── sample_notes.txt   # Example input file
```

This structure keeps the parsing logic independent from the CLI and separates rules, models, and I/O utilities into modular components that are easier to test and extend.

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

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run linting:

```bash
ruff check .
ruff format --check .
```

Run tests:

```bash
pytest
```

## Testing

```bash
python -m pytest
```

## Current Scope and Limitations

This project is intentionally a lightweight rule-based baseline for short symptom-focused clinical text. It does not aim to fully parse long clinical notes or resolve all complex linguistic structure.

It works best on short symptom-focused text snippets and can be extended with:

- richer symptom lexicons
- more robust scope handling for negation
- section-aware parsing
- better attachment rules for modifiers in multi-symptom sentences
- optional FHIR-style schema output

## Generative AI Usage

Generative AI usage for this project is documented in `AI_USAGE.md`.
