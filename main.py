import sys
from pathlib import Path
from row.row import Row
from readers.file import read_table
from cli import ID_TYPES, CLI_ARGS, parse_cli_args
from database.connection import query
from database.queries import SPRIDEN_ALL, SPRIDEN_REC

""" 10/29/2026
Intention: build a CLI where I can pass an Excel or CSV file with a Banner ID, PIDM, 
or SSN column, join that dataset to a result set of BIDs, PIDMs, and SSNs, and choose 
which of the other two columns to insert at the front of the dataset. It will produce
an identical file (type retained) with the only difference being the addition of the new columns
"""

DESC = 'enrich a dataset containing a student ID column with another type of student ID'

def s_strip(s: str) -> str:
    return s.replace('"', '').replace("'", '').strip().lower()

def extract_ids(rows: list[Row], column_name: str) -> list:
    for key in rows[0]:
        if s_strip(key) == s_strip(column_name):
            return [s_strip(row[key]) for row in rows]
        raise ValueError(f"'{column_name}' not found in headers: {rows[0]}")

def make_query(opt='current', little: int | None = None) -> str:
    match opt:
        case 'current': return SPRIDEN_REC(little)
        case 'all': return SPRIDEN_ALL(little)

# ENTRYPOINT
def main():
    args = parse_cli_args('enrich', DESC, CLI_ARGS)

    if args.dry:
        print('dry execution')
        sys.exit(0)

    spriden_query = make_query(args.query, args.little)

    print(f'+ reading rows from {args.file_in}...')
    try:
        rows = read_table(Path(args.file_in))
    except Exception as err:
        print(f'  - error reading {args.file_in}: {err}')
        sys.exit(1)
    print(f'  + {len(rows)} read from {args.file_in}')

    print(f'+ extracting {ID_TYPES[args.id_in]}s from {args.file_in}...')    
    try:
        ids = extract_ids(rows, args.id_column)
    except Exception as err:
        print(f'  - error extracting {ID_TYPES[args.id_in]}s from {args.file_in}: {err}')
        sys.exit(1)
    print(f'  + {len(ids)} {ID_TYPES[args.id_in]}s read from {args.file_in}')

    print('+ querying database for alternate IDs...')
    try:
        db_rows = query(spriden_query, batch_size=args.db_batch_size)
    except Exception as err:
        print(f'  - error querying for alternate IDs: {err}')
        sys.exit(1)

    print(f'  + {len(db_rows)} returned from database')
    
if __name__=="__main__":
    main()