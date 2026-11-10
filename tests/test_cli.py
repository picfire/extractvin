import csv
import datetime
import os
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from vininfo.cli import entry_point
from vininfo.csvlog import CSV_FIELDS

VIN = "1M8GDM9AXKP042788"


def test_show_appends_csv_record_and_writes_header_once(tmp_path):
    csv_path = tmp_path / "history.csv"
    runner = CliRunner()

    first_result = runner.invoke(entry_point, ["show", VIN, "--csv-file", str(csv_path)])
    second_result = runner.invoke(entry_point, ["show", VIN, "--csv-file", str(csv_path)])

    assert first_result.exit_code == 0
    assert second_result.exit_code == 0
    assert "Basic:" in first_result.output

    with csv_path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))

    assert tuple(rows[0]) == CSV_FIELDS
    assert len(rows) == 3
    assert rows[1][:4] == [VIN, "United States", "Mercury", "North America"]
    assert datetime.datetime.fromisoformat(rows[1][5]).tzinfo is not None
    assert rows[1][:5] == rows[2][:5]
    assert csv_path.stat().st_mode & 0o777 == 0o600


def test_show_writes_header_to_existing_empty_file(tmp_path):
    csv_path = tmp_path / "history.csv"
    csv_path.touch()

    result = CliRunner().invoke(entry_point, ["show", VIN, "--csv-file", str(csv_path)])

    assert result.exit_code == 0

    with csv_path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))

    assert rows[0] == list(CSV_FIELDS)
    assert len(rows) == 2


def test_show_invalid_vin_does_not_create_history(tmp_path):
    csv_path = tmp_path / "history.csv"

    result = CliRunner().invoke(entry_point, ["show", "invalid", "--csv-file", str(csv_path)])

    assert result.exit_code != 0
    assert not csv_path.exists()


def test_show_reports_write_error_after_printing_vin(tmp_path):
    result = CliRunner().invoke(entry_point, ["show", VIN, "--csv-file", str(tmp_path)])

    assert result.exit_code == 1
    assert "Basic:" in result.output
    assert "Could not write CSV history" in result.output


def test_history_displays_last_records_and_rejects_bad_limits(tmp_path):
    csv_path = tmp_path / "history.csv"
    runner = CliRunner()
    runner.invoke(entry_point, ["show", VIN, "--csv-file", str(csv_path)])
    runner.invoke(entry_point, ["show", "WBA71DC010CH14720", "--csv-file", str(csv_path)])

    result = runner.invoke(entry_point, ["history", "--csv-file", str(csv_path), "--last", "1"])
    zero_result = runner.invoke(entry_point, ["history", "--csv-file", str(csv_path), "--last", "0"])
    text_result = runner.invoke(entry_point, ["history", "--csv-file", str(csv_path), "--last", "many"])

    assert result.exit_code == 0
    assert "WBA71DC010CH14720" in result.output
    assert VIN not in result.output
    assert zero_result.exit_code != 0
    assert text_result.exit_code != 0


def test_history_reports_missing_or_malformed_file(tmp_path):
    missing_result = CliRunner().invoke(entry_point, ["history", "--csv-file", str(tmp_path / "missing.csv")])
    malformed_path = tmp_path / "malformed.csv"
    malformed_path.write_text("vin,country,manufacturer,region,years,timestamp\nshort,row\n", encoding="utf-8")

    malformed_result = CliRunner().invoke(entry_point, ["history", "--csv-file", str(malformed_path)])

    assert missing_result.exit_code == 1
    assert "run \"vininfo show\" first" in missing_result.output
    assert malformed_result.exit_code == 1
    assert "line 2" in malformed_result.output
    assert VIN not in malformed_result.output


def test_separate_processes_append_complete_records(tmp_path):
    csv_path = tmp_path / "history.csv"
    source_path = Path(__file__).parents[1] / "src"
    script = (
        "import sys; "
        "sys.path.insert(0, sys.argv[1]); "
        "from pathlib import Path; "
        "from vininfo.csvlog import append_record; "
        "[append_record(Path(sys.argv[2]), (sys.argv[3], 'US', 'Ford', 'North America', '2026', sys.argv[3])) "
        "for _ in range(20)]"
    )
    processes = [
        subprocess.Popen(
            [sys.executable, "-c", script, str(source_path), str(csv_path), f"VIN{index}"],
            cwd=tmp_path,
            env=os.environ.copy(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        for index in range(2)
    ]

    errors = [process.communicate()[1] for process in processes]

    assert [process.returncode for process in processes] == [0, 0], errors

    with csv_path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))

    assert rows[0] == list(CSV_FIELDS)
    assert len(rows) == 41
    assert {row[0] for row in rows[1:]} == {"VIN0", "VIN1"}