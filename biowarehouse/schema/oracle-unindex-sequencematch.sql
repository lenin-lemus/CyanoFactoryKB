alter session set ddl_lock_timeout = 1000000;
drop INDEX SM_QUERYWID;
drop INDEX SM_MATCHWID;
drop INDEX SM_COMPUTATIONWID;
drop INDEX SM_EVALUE;
drop INDEX SM_PVALUE;
drop INDEX SM_PIDENTICAL;
drop INDEX SM_PSIMILAR;
drop INDEX SM_RANK;
drop INDEX SM_LENGTH;
drop INDEX SM_QSTART_QEND;
drop INDEX SM_QEND;
drop INDEX SM_MSTART_MEND;
drop INDEX SM_MEND;
commit;

