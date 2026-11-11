# QUERIES MUST SELECT BANNER ID, PIDM, AND SSN IN THAT ORDER
from cli import ID_TYPES

def _fetch_only(num=100): return f'fetch first {num} rows only'

def SPRIDEN_ALL(little: int | None = None): return f"""
select spriden_id as bid, spriden_pidm as pidm, spbpers_ssn as ssn, spriden_last_name || ', ' || spriden_first_name as name
from spriden join spbpers on spbpers_pidm = spriden_pidm where spriden_change_ind is null 
{_fetch_only(little) if little is not None else ""}
"""

def SPRIDEN_REC(little: int | None = None): return f"""
select spriden_id as bid, spriden_pidm as pidm, spbpers_ssn as ssn, spriden_last_name || ', ' || spriden_first_name as name
from spriden join spbpers on spbpers_pidm = spriden_pidm 
-- and spbpers_ssn is null
where spriden_change_ind is null
and exists (
    select 1 from sgbstdn a
    where sgbstdn_pidm = spriden_pidm
    and sgbstdn_stst_code in ('AS', 'IL', 'P1')
    and sgbstdn_term_code_eff between to_char(sysdate, 'YYYY') - 8 || '20' and to_char(sysdate, 'YYYY') || '20'
)
or exists (
    select 1 from saradap
    where saradap_pidm = spriden_pidm
    and saradap_apst_code in ('D')
    and saradap_term_code_entry between to_char(sysdate, 'YYYY') - 8 || '20' and to_char(sysdate, 'YYYY') || '20'
)
{_fetch_only(little) if little is not None else ""}
"""

def SPRIDEN_TEST(test_bid: str): return f"""
select spriden_id as bid, spriden_pidm as pidm, spbpers_ssn as ssn, spriden_last_name || ', ' || spriden_first_name as name
from spriden join spbpers on spbpers_pidm = spriden_pidm 
where spriden_id = '{test_bid}' and spriden_change_ind is null
"""

MAX_IN = 1000

def QUERY_IDS(id_type: str, ids: list[str], little: int | None = None) -> tuple[str, dict]:
    if id_type not in ID_TYPES:
        raise ValueError(f'id_type must be one of {list(ID_TYPES)}')
    ids = list(dict.fromkeys(ids))
    if not ids:
        raise ValueError('no ids to query')

    col = ID_TYPES[id_type]['col']
    params, groups = {}, []
    for start in range(0, len(ids), MAX_IN):
        names = []
        for n, value in enumerate(ids[start:start + MAX_IN], start):
            params[f'id{n}'] = value
            names.append(f':id{n}')
        groups.append(f"{col} in ({', '.join(names)})")

    sql = f"""
select spriden_id as bid, spriden_pidm as pidm, spbpers_ssn as ssn,
       spriden_last_name || ', ' || spriden_first_name as name
from spriden join spbpers on spbpers_pidm = spriden_pidm
where spriden_change_ind is null
and ({' or '.join(groups)})
{_fetch_only(little) if little is not None else ""}
"""
    return sql, params