from typing import Any
import os
import sys
import argparse
import oracledb # import oracle library and explicitly set client as thick mode is required
from pathlib import Path
from readers.file import read_table
oracledb.init_oracle_client(lib_dir="/Users/dekockjt/oracle/instantclient_23_26")

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

Row = dict[str, Any]

SPRIDEN_ALL = """
select spriden_id as bid, spriden_pidm as pidm, spbpers_ssn as ssn
from spriden join spbpers on spbpers_pidm = spriden_pidm 
where spriden_change_ind is null
"""

def getParsedArgs():
    parser = argparse.ArgumentParser(
        prog='enrich',
        description='erich a dataset with additional student identifier types'
    )
    parser.add_argument('-d', '--dry', action='store_true')
    parser.add_argument('-i', '--id-in', default='bid', choices=list(ID_TYPES), 
        help='the ID type in the existing file to join to')
    parser.add_argument('-n', '--id-column', default='Banner ID', help='name of the column in the input file with ID')
    parser.add_argument('-f', '--file-in', default='test.csv', help='the input file')
    parser.add_argument('-j', '--join-type', default='left', choices=['left', 'inner'], 
        help='join type: preserve all rows from file or only write joined rows')
    parser.add_argument('-b', '--bid', action='store_true', help='add Banner ID column') 
    parser.add_argument('-p', '--pidm', action='store_true', help='add PIDM column')
    parser.add_argument('-c', '--csv', action='store_true', help='save output as CSV')
    parser.add_argument('-x', '--xl', action='store_true', help='save output as Excel')
    parser.add_argument('-a', '--all', action='store_true', 
        help='Join against full SPRIDEN query - default limits to students enrolled in the last several years')
    parser.add_argument('-o', '--out-dir', action='store_true', help='directory to write the output file')
    
    return parser.parse_args()

def s_strip(s: str) -> str:
    return s.replace('"', '').replace("'", '').strip().lower()

def extract_ids(rows: list[Row], column_name: str) -> list:
    for key in rows[0]:
        if s_strip(key) == s_strip(column_name):
            return [s_strip(row[key]) for row in rows]
        raise ValueError(f"'{column_name}' not found in headers: {rows[0]}")

def connect_db() -> oracledb.Connection:
    user = os.environ['ORA_USER']
    pswd = os.environ['ORA_PASS']
    port = os.environ['ORA_PORT']
    host = os.environ['ORA_HOST']
    name = os.environ['ORA_NAME']
    dsn = f'{host}:{port}/{name}'
    return oracledb.connect(user=user, password=pswd, dsn=dsn)

def main():
    args = getParsedArgs()
    if args.dry:
        print('dry execution')
        sys.exit(0)

    rows = read_table(Path(args.file_in))
    print(rows)

    ids = extract_ids(rows, args.id_column)
    print(ids)

if __name__=="__main__":
    main()