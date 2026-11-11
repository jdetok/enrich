import re
from row.row import Row
from cli import ID_TYPES

def s_strip(s: str) -> str:
    if s is None: return ''
    return s.replace('"', '').replace("'", '').strip().lower()

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

def enrich(
    rows: list[Row], 
    id_column: str, 
    new_column: str, 
    lookup: dict[str, str], 
    keep_unmatched=True
) -> tuple[list[Row], int]:
    key = find_key(rows[0], id_column)
    if s_strip(new_column) in {s_strip(k) for k in rows[0]}:
        raise ValueError(f"column '{new_column}' already exists in the input file")
    out, unmatched = [], 0
    for row in rows: 
        match = lookup.get(s_strip(row[key]))
        if match is None:
            unmatched += 1
            if not keep_unmatched:
                continue
        out.append({new_column: match, **row})
    return out, unmatched

def extract_ids(rows: list[Row], id_col: str, id_type) -> list[str]:
    key = find_key(rows[0], id_col)
    ids = [str(row[key]).strip() for row in rows if row.get(key) not in [None, '']]
    rx = re.compile(ID_TYPES[id_type]['pattern']) if ID_TYPES[id_type].get('pattern') else None
    return [i for i in ids if rx is None or rx.fullmatch(i)]
