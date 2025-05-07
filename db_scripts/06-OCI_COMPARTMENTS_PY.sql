CREATE TABLE OCI_FOCUS_REPORTS.OCI_COMPARTMENTS_PY 
    ( 
     "Compartment_ID"  VARCHAR2 (4000) , 
     "Name"            VARCHAR2 (4000) , 
     "Description"     VARCHAR2 (4000) , 
     "Lifecycle_State" VARCHAR2 (4000) , 
     "Time_Created"    VARCHAR2 (4000) , 
     "Parent_ID"       VARCHAR2 (4000) , 
     PARENT            VARCHAR2 (4000) , 
     "Path"            VARCHAR2 (4000) , 
     "Tenancy_ID"      VARCHAR2 (2000) 
    ) 
    TABLESPACE DATA 
    LOGGING 
;