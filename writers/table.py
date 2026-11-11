from openpyxl import Workbook
from pathlib import Path
import csv

def write_table(rows: list[dict], filename: Path, fieldnames=None, sheet: str | None = None):
    if not rows:
        raise ValueError('No rows to write')
    fieldnames = fieldnames or list(rows[0].keys())

    if filename.suffix == '.csv':
        return _write_csv(rows, filename, fieldnames)
    elif '.xls' in filename.suffix:
        return _write_excel(rows, filename, fieldnames, sheet)
    raise ValueError(f'File type ({filename.suffix}) must be compatible CSV or Excel')

def _write_csv(rows: list[dict], filename, fieldnames=None):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)

def _write_excel(rows: list[dict], filename, fieldnames=None, sheet: str | None = None):
    wb = Workbook()
    ws = wb.active
    ws.title = (sheet if sheet is not None else 'Sheet1')[:31] # sheet name capped at 31 chars
    ws.append(fieldnames)

    for row in rows:
        ws.append([row.get(k) for k in fieldnames])

    # force number format to text to preserve banner ID leading zeroes
    for col in ws.iter_cols(min_row=2):
        for cell in col:
            if isinstance(cell.value, str):
                cell.number_format = '@'

    wb.save(filename)
