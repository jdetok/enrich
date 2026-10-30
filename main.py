import sys
from pathlib import Path
from row.row import Row
from cli.cli import parse_cli_args
from readers.file import read_table
from database.queries import SPRIDEN_ALL, SPRIDEN_RECENT
from database.connection import query


""" 10/29/2026
Intention: build a CLI where I can pass an Excel or CSV file with a Banner ID, PIDM, 
or SSN column, join that dataset to a result set of BIDs, PIDMs, and SSNs, and choose 
which of the other two columns to insert at the front of the dataset. It will produce
an identical file (type retained) with the only difference being the addition of the new columns
"""

ID_TYPES = {
    'bid': 'Banner ID',
    'pidm': 'PIDM',
    'ssn': 'SSN',
}

CLI_ARGS = {
    'd': {'long': 'dry', 'action': 'store_true', 'help': 'execute a dry run'},
    'n': {'long': 'id-column', 'default': 'bid', 'help': 'the ID type in the existing file to join to'},
    'f': {'long': 'file-in', 'default': 'test.csv', 'help': 'the ID type in the existing file to join to'},
    'b': {'long': 'bid', 'action': 'store_true', 'help': 'add Banner ID column'},
    'p': {'long': 'pidm', 'action': 'store_true', 'help': 'add PIDM column'},
    's': {'long': 'ssn', 'action': 'store_true', 'help': 'add SSN column'},
    'c': {'long': 'save-csv', 'action': 'store_true', 'help': 'save output file as CSV regardless of input type'},
    'x': {'long': 'save-xl', 'action': 'store_true', 'help': 'save output file as Excel regardless of input type'},
    'z': {'long': 'db-batch-size', 'default': 15_000, 'help': 'set the batch array size for the oracledb driver'},
    'i': {
        'long': 'id-in', 'default': 'bid', 'choices': list(ID_TYPES),
        'help': 'the ID type in the existing file to join to'
    },
    'a': {
        'long': 'all-spriden', 'action': 'store_true', 
        'help': 'join against full SPRIDEN query - default limits to students enrolled in the last several years'
    },
    'j': {
        'long': 'join-type', 'default': 'left', 'choices': ['left', 'inner'], 
        'help': 'join type: preserve all rows from file or only write joined rows'
    },
}

def s_strip(s: str) -> str:
    return s.replace('"', '').replace("'", '').strip().lower()

def extract_ids(rows: list[Row], column_name: str) -> list:
    for key in rows[0]:
        if s_strip(key) == s_strip(column_name):
            return [s_strip(row[key]) for row in rows]
        raise ValueError(f"'{column_name}' not found in headers: {rows[0]}")

def main():
    args = parse_cli_args(
        'enrich', 
        'enrich a dataset containing a student ID column with another type of student ID',
        CLI_ARGS
    )

    if args.dry:
        print('dry execution')
        sys.exit(0)

    spriden_query = SPRIDEN_ALL if args.all_spriden else SPRIDEN_RECENT

    rows = read_table(Path(args.file_in))
    print(rows)

    ids = extract_ids(rows, args.id_column)
    print(ids)

    queryRows = query(spriden_query, batch_size=args.db_batch_size)
    print(len(queryRows))
    

if __name__=="__main__":
    main()