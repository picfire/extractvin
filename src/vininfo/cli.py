import sys
from datetime import datetime, timezone
from pathlib import Path

import click

from vininfo import VERSION, Vin
from vininfo.csvlog import CSV_FIELDS, CsvFormatError, append_record, read_records


@click.group()
@click.version_option(version=VERSION)
def entry_point():
    """vininfo command line utilities."""


@entry_point.command()
@click.argument('vin')
@click.option("--csv-file", type=click.Path(path_type=Path), default=Path("vininfo.csv"), show_default=True)
def show(vin, csv_file):
    """Show information for VIN"""
    num = Vin(vin)

    click.secho('Basic:')

    def out(annotatable):
        for k, v in annotatable.annotate().items():
            click.secho(f'{k}: ', fg='green', nl=False)
            click.secho(v)

    out(num)

    details = num.details

    if details:
        click.secho('')
        click.secho('Details:')
        out(details)

    record = (
        num.num,
        num.country or '',
        num.manufacturer,
        num.region or '',
        ', '.join(f'{year}' for year in num.years),
        datetime.now(tz=timezone.utc).isoformat(),
    )

    try:
        append_record(csv_file, record)
    except OSError as error:
        raise click.ClickException(f'Could not write CSV history: {error}') from error


@entry_point.command()
@click.option("--csv-file", type=click.Path(path_type=Path), default=Path("vininfo.csv"), show_default=True)
@click.option("--last", type=click.IntRange(min=1), default=None)
def history(csv_file, last):
    """Show previously recorded VIN information."""
    try:
        records = read_records(csv_file)
    except FileNotFoundError as error:
        raise click.ClickException("CSV history file not found; run \"vininfo show\" first") from error
    except (OSError, CsvFormatError) as error:
        raise click.ClickException(f'Could not read CSV history: {error}') from error

    if last is not None:
        records = records[-last:]

    table = [CSV_FIELDS, *records]
    widths = [max(len(row[index]) for row in table) for index in range(len(CSV_FIELDS))]

    for row in table:
        click.echo('  '.join(value.ljust(widths[index]) for index, value in enumerate(row)))


@entry_point.command()
@click.argument('vin')
def check(vin):
    """Perform VIN checksum validation"""

    if Vin(vin).verify_checksum():
        click.secho('Checksum is valid', fg='green')
    else:
        click.secho('Checksum is not valid', fg='red', err=True)
        sys.exit(1)


def main():
    entry_point(obj={})


if __name__ == '__main__':
    main()
