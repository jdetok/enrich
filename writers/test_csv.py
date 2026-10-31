import csv
from collections.abc import Sequence
from pathlib import Path
from typing import Any

def make_test_csv(
    header: Sequence[str],
    rows: Sequence[Sequence[Any]],
    path: str | Path = 'test.csv',
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists() and path.stat().st_size > 0:
        with path.open('r', newline='', encoding='utf-8') as f:
            existing = next(csv.reader(f), [])

        missing = set(header) - set(existing)
        if missing:
            raise ValueError(f'{path} has no column(s) {sorted(missing)}; columns are {existing}')

        # add a newline if the file doesn't end with one
        with path.open('rb+') as f:
            f.seek(-1, 2)
            if f.read(1) not in (b'\n', b'\r'):
                f.write(b'\r\n')

        # align each row to the file's column order, blanks for the rest
        aligned = [
            [dict(zip(header, row)).get(col, '') for col in existing]
            for row in rows
        ]
        with path.open('a', newline='', encoding='utf-8') as f:
            csv.writer(f, quoting=csv.QUOTE_ALL).writerows(aligned)
    else:
        with path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(header)
            writer.writerows(rows)
    return path

def remove_rows_where(path: str | Path, column: str, value: str) -> int:
    path = Path(path)
    with path.open('r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    kept = [r for r in rows if r[column] != value]
    removed = len(rows) - len(kept)

    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(kept)
    return removed