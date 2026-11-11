import sys
from pathlib import Path
from datetime import datetime
from readers.file import read_table
from test import setup_test_mode
from cli import ID_TYPES, CLI_ARGS, parse_cli_args
from enrich.enrich import build_lookup, enrich
from writers.table import write_table
from database.connection import query

from database.queries import SPRIDEN_ALL, SPRIDEN_REC, SPRIDEN_TEST

""" 10/29/2026
Intention: build a CLI where I can pass an Excel or CSV file with a Banner ID, PIDM, 
or SSN column, join that dataset to a result set of BIDs, PIDMs, and SSNs, and choose 
which of the other two columns to insert at the front of the dataset. It will produce
an identical file (type retained) with the only difference being the addition of the new columns
"""

DESC = 'enrich a dataset containing a student ID column with another type of student ID'
OUT_DIR = 'out'

def outfile(in_name: Path): 
    return Path(f'./{OUT_DIR}/{in_name.stem}_{datetime.now().strftime('%m%d%Y_%H%M%S')}{in_name.suffix}')

def make_query(opt='current', little: int | None = None, test_bid: str | None = None) -> str:
    match opt:
        case 'current': return SPRIDEN_REC(little)
        case 'all': return SPRIDEN_ALL(little)
        case 'test': return SPRIDEN_TEST(test_bid)

# ENTRYPOINT
def main():
    args = parse_cli_args('enrich', DESC, CLI_ARGS)

    if args.dry:
        print('dry execution')
        sys.exit(0)

    test_bid = None
    if args.query == 'test':
        test_bid = setup_test_mode()

    spriden_query = make_query(args.query, args.little, test_bid)

    in_type, out_type = ID_TYPES[args.id_in], ID_TYPES[args.id_out]
    out_file = outfile(Path(args.file_in))

    print(f'+ reading rows from {args.file_in}...')
    try:
        rows = read_table(Path(args.file_in))
        print(f'  + {len(rows)} read from {args.file_in}')
    except Exception as err:
        print(f'  - error reading {args.file_in}: {err}')
        sys.exit(1)
    
    print('+ querying database for alternate IDs...')
    try:
        db_rows = query(spriden_query, batch_size=args.db_batch_size)
        print(f'  + {len(db_rows)} rows returned from database')
    except Exception as err:
        print(f'  - error querying for alternate IDs: {err}')
        sys.exit(1)

    print(f'+ attempting {args.join_type} join on {in_type['long']}...')
    try:
        lookup = build_lookup(
            db_rows, args.id_in, out_type['idx'],
            in_type.get('pattern'), out_type.get('pattern'),
        )
        enriched, unmatched = enrich(
            rows, args.id_column, out_type['long'], lookup, 
            keep_unmatched=True if args.join_type == 'left' else False
        )
        print(f'  + {len(enriched)} matched, {unmatched} unmatched')
    except Exception as err:
        print(f'  - error joining datasets: {err}')
        sys.exit(1)
    
    try:
        write_table(enriched, out_file)
    except Exception as err:
        print(f'  - error attempting to write output file ')
        sys.exit(1)

    print(f'+ wrote {len(enriched)} rows to {out_file}')

if __name__=="__main__":
    main()