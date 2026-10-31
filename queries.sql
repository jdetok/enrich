select spriden_id as bid, spriden_pidm as pidm, spbpers_ssn as ssn
from spriden join spbpers on spbpers_pidm = spriden_pidm 
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
;
select * from saradap;
select * from stvapst;