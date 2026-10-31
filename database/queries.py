# QUERIES MUST SELECT BANNER ID, PIDM, AND SSN IN THAT ORDER

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