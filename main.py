import sys
from pathlib import Path
from datetime import datetime
from test import setup_test_mode
from readers.table import read_table
from writers.table import write_table
from database.connection import query
from database.queries import QUERY_IDS
from cli import ID_TYPES, CLI_ARGS, parse_cli_args
from enrich import build_lookup, enrich, extract_ids

"""
Read a CSV/Excel file containing a column with Banner IDs, SSNs, or PIDMs and enrich the file with
an additional identifier column (e.g. add Banner IDs to a file of SSNs)
"""

NAME = 'enrich'
DESC = 'enrich a dataset containing a student ID column with another type of student ID'
OUT_DIR = 'out'

def outfile(in_name: Path): 
    return Path(f'./{OUT_DIR}/{in_name.stem}_{datetime.now().strftime('%m%d%Y_%H%M%S')}{in_name.suffix}')

# ENTRYPOINT
def main():
    args = parse_cli_args(NAME, DESC, CLI_ARGS)

    in_file = Path(args.file_in)
    out_file = outfile(in_file)
    in_id, out_id = args.id_in, args.id_out
    in_col = args.id_column
    in_type, out_type = ID_TYPES[in_id], ID_TYPES[out_id]

    if args.dry:
        print('dry execution')
        sys.exit(0)

    if args.query == 'test':
        setup_test_mode()

    # read input file data
    try:
        rows = read_table(in_file)
        print(f'+ {len(rows)} read from {in_file}')
    except Exception as err:
        print(f'- error reading {in_file}: {err}')
        sys.exit(1)

    # build query to spriden with the IDs from the file
    ids = extract_ids(rows, in_col, in_id)
    spriden_query, params = QUERY_IDS(in_id, ids)

    # run query
    print('+ querying database for alternate IDs...')
    try:
        db_rows = query(spriden_query, params, batch_size=args.db_batch_size)
        print(f'  + {len(db_rows)} rows returned from database')
    except Exception as err:
        print(f'  - error querying for alternate IDs: {err}')
        sys.exit(1)

    # create enriched dataset
    print(f'+ attempting {args.join_type} join on {in_type['long']}...')
    try:
        lookup = build_lookup(
            db_rows, in_id, out_type['idx'],
            in_type.get('pattern'), out_type.get('pattern'),
        )
        enriched, unmatched = enrich(
            rows, in_col, out_type['long'], lookup, 
            keep_unmatched=True if args.join_type == 'left' else False
        )
        print(f'  + {len(enriched)} matched, {unmatched} unmatched')
    except Exception as err:
        print(f'  - error joining datasets: {err}')
        sys.exit(1)

    # write enriched dataset
    try:
        write_table(enriched, out_file)
    except Exception as err:
        print(f'  - error attempting to write output file ')
        sys.exit(1)

    print(f'+ wrote {len(enriched)} rows to {out_file}')

if __name__=="__main__":
    main()