"""Command-line interface for the clinical text parser."""

from __future__ import annotations

import argparse
from pathlib import Path

from clinical_text_parser.io import dump_json, read_text_lines
from clinical_text_parser.parser import ClinicalTextParser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract structured symptom information from short clinical text."
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--text", help="Clinical text snippet to parse.")
    source_group.add_argument(
        "--input-file",
        type=Path,
        help="Path to a text file containing one clinical note per line.",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        help="Optional JSON output path. If omitted, results are printed to stdout.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    parser = ClinicalTextParser()

    if args.text is not None:
        payload = parser.parse(args.text).to_dict()
    else:
        payload = [parser.parse(text).to_dict() for text in read_text_lines(args.input_file)]

    rendered = dump_json(payload, path=args.output_file)
    if args.output_file is None:
        print(rendered)
    return 0
