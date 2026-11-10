import csv
import os
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, TextIO

if sys.platform == "win32":
    import msvcrt
else:
    import fcntl

CSV_FIELDS = ("vin", "country", "manufacturer", "region", "years", "timestamp")


class CsvFormatError(ValueError):
    """The CSV history file does not match the expected format."""


@contextmanager
def _lock_file(file: TextIO) -> Iterator[None]:
    if sys.platform == "win32":
        position = file.tell()
        lock_position = 0x7FFFFFFF
        deadline = time.monotonic() + 10
        file.flush()
        os.lseek(file.fileno(), lock_position, os.SEEK_SET)

        while True:
            try:
                msvcrt.locking(file.fileno(), msvcrt.LK_NBLCK, 1)
                break
            except OSError as error:
                if time.monotonic() >= deadline:
                    file.seek(position)
                    raise TimeoutError("Timed out waiting for the CSV history lock") from error

                time.sleep(0.05)

        try:
            yield
        finally:
            file.flush()
            os.lseek(file.fileno(), lock_position, os.SEEK_SET)
            msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, 1)
            file.seek(position)
    else:
        fcntl.flock(file.fileno(), fcntl.LOCK_EX)

        try:
            yield
        finally:
            fcntl.flock(file.fileno(), fcntl.LOCK_UN)


def append_record(path: Path, record: tuple[str, ...]) -> None:
    """Append one VIN record, writing the header when the file is empty."""
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    file_descriptor = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)

    with os.fdopen(file_descriptor, "a", newline="", encoding="utf-8") as file:
        with _lock_file(file):
            writer = csv.writer(file)

            if os.fstat(file.fileno()).st_size == 0:
                writer.writerow(CSV_FIELDS)

            writer.writerow(record)
            file.flush()


def read_records(path: Path) -> list[tuple[str, ...]]:
    """Read and validate every record in a VIN history file."""
    with path.open("r", newline="", encoding="utf-8") as file:
        with _lock_file(file):
            reader = csv.reader(file, strict=True)

            try:
                header = next(reader)
            except StopIteration as error:
                raise CsvFormatError("CSV format error at line 1: missing header") from error
            except csv.Error as error:
                raise CsvFormatError(f"CSV format error at line {reader.line_num}: {error}") from error

            if tuple(header) != CSV_FIELDS:
                raise CsvFormatError("CSV format error at line 1: unexpected header")

            records = []

            while True:
                line_number = reader.line_num + 1

                try:
                    record = next(reader)
                except StopIteration:
                    break
                except csv.Error as error:
                    raise CsvFormatError(f"CSV format error at line {reader.line_num}: {error}") from error

                if len(record) != len(CSV_FIELDS):
                    raise CsvFormatError(f"CSV format error at line {line_number}: expected 6 fields")

                records.append(tuple(record))

            return records