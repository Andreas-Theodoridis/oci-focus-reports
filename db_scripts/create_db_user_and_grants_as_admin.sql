CREATE USER "OCI_FOCUS_REPORTS" DEFAULT COLLATION "USING_NLS_COMP" 
   DEFAULT TABLESPACE "DATA"
   TEMPORARY TABLESPACE "TEMP"
   IDENTIFIED BY &1;
ALTER USER "OCI_FOCUS_REPORTS" QUOTA UNLIMITED ON "DATA";
GRANT "CONNECT" TO "OCI_FOCUS_REPORTS";
GRANT "RESOURCE" TO "OCI_FOCUS_REPORTS";
GRANT "DATAPUMP_CLOUD_EXP" TO "OCI_FOCUS_REPORTS";
GRANT "DATAPUMP_CLOUD_IMP" TO "OCI_FOCUS_REPORTS";
GRANT "DWROLE" TO "OCI_FOCUS_REPORTS";
GRANT "CONSOLE_DEVELOPER" TO "OCI_FOCUS_REPORTS";
GRANT "OML_DEVELOPER" TO "OCI_FOCUS_REPORTS";
GRANT EXECUTE ON "DBMS_CLOUD_PIPELINE" TO "OCI_FOCUS_REPORTS";
GRANT EXECUTE ON "DBMS_CLOUD_AI" TO "OCI_FOCUS_REPORTS";
GRANT EXECUTE ON "DBMS_CLOUD" TO "OCI_FOCUS_REPORTS";
GRANT EXECUTE ON DBMS_RESULT_CACHE TO OCI_FOCUS_REPORTS;
GRANT EXECUTE ON DBMS_CLOUD_PIPELINE TO "OCI_FOCUS_REPORTS";
GRANT EXECUTE ON CS_SESSION TO "OCI_FOCUS_REPORTS";
-- ADD ROLES
ALTER USER OCI_FOCUS_REPORTS DEFAULT ROLE CONSOLE_DEVELOPER,DWROLE,OML_DEVELOPER,CONNECT,RESOURCE;
-- REST ENABLE
BEGIN
    ORDS_ADMIN.ENABLE_SCHEMA(
        p_enabled => TRUE,
        p_schema => 'OCI_FOCUS_REPORTS',
        p_url_mapping_type => 'BASE_PATH',
        p_url_mapping_pattern => 'oci_focus_reports',
        p_auto_rest_auth=> FALSE
    );
    -- ENABLE DATA SHARING
    C##ADP$SERVICE.DBMS_SHARE.ENABLE_SCHEMA(
            SCHEMA_NAME => 'OCI_FOCUS_REPORTS',
            ENABLED => TRUE
    );
    commit;
END;
/
ALTER PROFILE "DEFAULT"
    LIMIT 
         PASSWORD_LIFE_TIME UNLIMITED;

EXEC DBMS_AUTO_INDEX.CONFIGURE('AUTO_INDEX_MODE','IMPLEMENT');
EXEC DBMS_AUTO_INDEX.CONFIGURE('AUTO_INDEX_SCHEMA','OCI_FOCUS_REPORTS', TRUE);
EXEC DBMS_CLOUD_ADMIN.DISABLE_RESOURCE_PRINCIPAL();
EXEC DBMS_CLOUD_ADMIN.ENABLE_RESOURCE_PRINCIPAL();
EXEC DBMS_CLOUD_ADMIN.ENABLE_RESOURCE_PRINCIPAL(username => 'OCI_FOCUS_REPORTS');
EXEC DBMS_CLOUD_ADMIN.DISABLE_RESOURCE_PRINCIPAL();
EXEC DBMS_CLOUD_ADMIN.ENABLE_RESOURCE_PRINCIPAL();
EXEC DBMS_CLOUD_ADMIN.ENABLE_RESOURCE_PRINCIPAL(username => 'OCI_FOCUS_REPORTS');
GRANT EXECUTE ON "ADMIN"."OCI$RESOURCE_PRINCIPAL" TO "OCI_FOCUS_REPORTS";
BEGIN
  -- Create the scheduler job.
  DBMS_SCHEDULER.CREATE_JOB (
    job_name          => 'GATHER_OCI_FOCUS_REPORTS_STATS',
    job_type          => 'PLSQL_BLOCK',
    job_action        => 'BEGIN
                            DBMS_STATS.GATHER_SCHEMA_STATS(
                              ownname             => ''OCI_FOCUS_REPORTS'',
                              estimate_percent  => DBMS_STATS.AUTO_SAMPLE_SIZE,  -- Let Oracle determine sample size
                              method_opt          => ''FOR ALL COLUMNS SIZE AUTO'',    -- Gather histograms as needed
                              degree              => NULL,         -- Use the default degree of parallelism
                              no_invalidate       => FALSE,       -- Invalidates dependent cursors
                              granularity         => ''AUTO''       -- Gather stats at appropriate level
                            );
                          END;',
    --start_date        => '04/19/2025 1:00:00', -- Example: Runs daily at 01:00 AM
    repeat_interval   => 'FREQ=DAILY;BYHOUR=01',  -- Can be DAILY, WEEKLY, MONTHLY, etc.  See DBMS_SCHEDULER documentation.
    end_date          => NULL,          -- No end date.  Change if needed.
    enabled           => TRUE,          -- The job is enabled and will run.
    comments          => 'Gather statistics for the OCI_FOCUS_REPORTS schema.'
  );
  COMMIT;
  DBMS_OUTPUT.PUT_LINE('Scheduler job "GATHER_OCI_FOCUS_REPORTS_STATS" created and enabled.');

EXCEPTION
  WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('Error creating scheduler job: ' || SQLERRM);
    ROLLBACK;
END;
/
EXIT