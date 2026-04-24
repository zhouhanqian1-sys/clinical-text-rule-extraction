from __future__ import annotations

import json

from clinical_text_parser.cli.main import main


# Test parsing clinical text passed directly from the command line
def test_cli_text_output(capsys) -> None:
    exit_code = main(["--text", "Patient has cough."])
    captured = capsys.readouterr()

    assert exit_code == 0
    output = json.loads(captured.out)
    assert output["mentions"][0]["symptom"] == "cough"
    assert output["mentions"][0]["negated"] is False


# Test parsing clinical text from an input file and writing results to an output file
def test_cli_file_output(tmp_path) -> None:
    input_file = tmp_path / "notes.txt"
    output_file = tmp_path / "results.json"

    input_file.write_text(
        "Patient has cough.\nPatient denies fever.\n",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--input-file",
            str(input_file),
            "--output-file",
            str(output_file),
        ]
    )

    assert exit_code == 0
    result = json.loads(output_file.read_text(encoding="utf-8"))
    assert len(result) == 2
    assert result[0]["mentions"][0]["symptom"] == "cough"
    assert result[1]["mentions"][0]["symptom"] == "fever"
    assert result[1]["mentions"][0]["negated"] is True


# Test that blank lines in the input file are skipped and do not affect results
def test_cli_skips_blank_lines_in_input_file(tmp_path) -> None:
    input_file = tmp_path / "notes.txt"
    output_file = tmp_path / "results.json"

    input_file.write_text(
        "Patient has cough.\n\n   \nPatient denies fever.\n",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--input-file",
            str(input_file),
            "--output-file",
            str(output_file),
        ]
    )

    assert exit_code == 0
    result = json.loads(output_file.read_text(encoding="utf-8"))
    assert len(result) == 2
    assert result[0]["mentions"][0]["symptom"] == "cough"
    assert result[1]["mentions"][0]["symptom"] == "fever"
