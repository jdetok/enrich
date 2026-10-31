import os
import re
import sys
import atexit
from pathlib import Path
from row.row import Row
from readers.file import read_table
from writers.test_csv import make_test_csv, remove_rows_where
from database.connection import query
from cli import ID_TYPES, CLI_ARGS, parse_cli_args
from database.queries import SPRIDEN_ALL, SPRIDEN_REC, SPRIDEN_TEST

""" 10/29/2026
Intention: build a CLI where I can pass an Excel or CSV file with a Banner ID, PIDM, 
or SSN column, join that dataset to a result set of BIDs, PIDMs, and SSNs, and choose 
which of the other two columns to insert at the front of the dataset. It will produce
an identical file (type retained) with the only difference being the addition of the new columns
"""

DESC = 'enrich a dataset containing a student ID column with another type of student ID'
TEST_BID_ENV = 'TEST_BANNER_ID'
TEST_CSV = 'test.csv'
TEST_COL = 'bid'

def s_strip(s: str) -> str:
    if s is None: return ''
    return s.replace('"', '').replace("'", '').strip().lower()

def extract_ids(rows: list[Row], column_name: str, pattern: str | re.Pattern | None = None) -> list:
    if not rows:
        raise ValueError('no rows to extract from')
    target = s_strip(column_name).lower()
    lookup = {s_strip(k).lower(): k for k in rows[0]}
    if target not in lookup:
        raise ValueError(f"'{target}' not found in headers: {list(lookup)}")
    key = lookup[target]

    rx = re.compile(pattern) if isinstance(pattern, str) else pattern

    ids = []
    for row in rows:
        if row[key] is None:
            continue
        value = s_strip(row[key])
        if rx is None or rx.fullmatch(value):
            ids.append(value)
    return ids
    # return [s_strip(row[key]) for row in rows]

def make_query(opt='current', little: int | None = None, test_bid: str | None = None) -> str:
    match opt:
        case 'current': return SPRIDEN_REC(little)
        case 'all': return SPRIDEN_ALL(little)
        case 'test': return SPRIDEN_TEST(test_bid)

def find_key(row: Row, column_name: str) -> str:
    target = s_strip(column_name)
    lookup = {s_strip(k): k for k in row}
    if target not in lookup:
        raise ValueError(f"'{target}' not found in headers: {list(lookup)}")
    return lookup[target]

def build_lookup(
    db_rows: list[Row], in_col: str, out_idx: int, 
    in_pattern: str | None = None, out_pattern: str | None = None
) -> dict[str, str]:
    if not db_rows:
        raise ValueError('no db rows')
    in_key = find_key(db_rows[0], in_col)
    out_key = list(db_rows[0])[out_idx]
    in_rx = re.compile(in_pattern) if in_pattern else None
    out_rx = re.compile(out_pattern) if out_pattern else None

    lookup: dict[str, str] = {}
    conflicts = 0
    for row in db_rows:
        if row[in_key] is None or row[out_key] is None:
            continue
        k, v = s_strip(row[in_key]), s_strip(row[out_key])
        if (in_rx and not in_rx.fullmatch(k)) or (out_rx and not out_rx.fullmatch(k)):
            continue
        if k in lookup and lookup[k] != v:
            conflicts += 1
            continue
        lookup[k] = v
    if conflicts:
        print(f'  ! {conflicts} input IDs mapped to more than one output ID (kept first)')
    return lookup

def enrich(rows: list[Row], id_column: str, new_column: str, lookup: dict[str, str]) -> tuple[list[Row], int]:
    key = find_key(rows[0], id_column)
    if s_strip(new_column) in {s_strip(k) for k in rows[0]}:
        raise ValueError(f"column '{new_column}' already exists in the input file")
    out, unmatched = [], 0
    for row in rows: 
        match = lookup.get(s_strip(row[key]))
        if match is None:
            unmatched += 1
        out.append({new_column: match, **row})
    return out, unmatched

def get_test_bid(bid_env_var=TEST_BID_ENV) -> str | None:
    test_bid = os.environ.get(bid_env_var)
    if test_bid is None:
        print(f'  ! {bid_env_var} not found in .env')
        return None
    return test_bid

def cleanup_test_mode(bid_env_var=TEST_BID_ENV, test_file: str | Path = TEST_CSV):
    print(f'+ cleaning up test mode - removing {bid_env_var} from {test_file}')
    removed = remove_rows_where(test_file, TEST_COL, get_test_bid(bid_env_var))
    print(f'  + removed {removed} rows containing {bid_env_var} from {test_file}')

def setup_test_mode(bid_env_var=TEST_BID_ENV) -> str | None:
    print(f'+ test mode - adding {bid_env_var} from .env file to {TEST_CSV}')
    test_bid = get_test_bid(bid_env_var)
    path = make_test_csv([TEST_COL], [[test_bid]])
    print(f'  + wrote {bid_env_var} to {path}')
    atexit.register(cleanup_test_mode, bid_env_var, path)
    return test_bid

# ENTRYPOINT
def main():
    args = parse_cli_args('enrich', DESC, CLI_ARGS)

    if args.dry:
        print('dry execution')
        sys.exit(0)

    if args.query == 'test':
        test_bid = setup_test_mode()

    spriden_query = make_query(args.query, args.little, test_bid)

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
        print(db_rows)
        print(f'  + {len(db_rows)} rows returned from database')
    except Exception as err:
        print(f'  - error querying for alternate IDs: {err}')
        sys.exit(1)
    
    in_type, out_type = ID_TYPES[args.id_in], ID_TYPES[args.id_out]
    print(f'+ joining on {in_type['long']}...')
    try:
        lookup = build_lookup(
            db_rows, args.id_in, out_type['idx'],
            in_type.get('pattern'), out_type.get('pattern'),
        )
        enriched, unmatched = enrich(rows, args.id_column, out_type['long'], lookup)
        print(f'  + {len(enriched) - unmatched} matched, {unmatched} unmatched')
    except Exception as err:
        print(f'  - error joining datasets: {err}')
        sys.exit(1)

    print(enriched)

if __name__=="__main__":
    main()