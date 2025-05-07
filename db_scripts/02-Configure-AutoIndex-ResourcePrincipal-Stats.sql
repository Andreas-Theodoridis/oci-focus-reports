EXEC DBMS_AUTO_INDEX.CONFIGURE('AUTO_INDEX_MODE','IMPLEMENT');
EXEC DBMS_AUTO_INDEX.CONFIGURE('AUTO_INDEX_SCHEMA','OCI_FOCUS_REPORTS', TRUE);
EXEC DBMS_CLOUD_ADMIN.DISABLE_RESOURCE_PRINCIPAL();
EXEC DBMS_CLOUD_ADMIN.ENABLE_RESOURCE_PRINCIPAL();
EXEC DBMS_CLOUD_ADMIN.ENABLE_RESOURCE_PRINCIPAL(username => 'OCI_FOCUS_REPORTS');
EXEC DBMS_CLOUD_ADMIN.DISABLE_RESOURCE_PRINCIPAL();
EXEC DBMS_CLOUD_ADMIN.ENABLE_RESOURCE_PRINCIPAL();
EXEC DBMS_CLOUD_ADMIN.ENABLE_RESOURCE_PRINCIPAL(username => 'OCI_FOCUS_REPORTS');
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

  -- Optional:  Grant execute privilege on the job to another user.  Remove this if not needed.
  -- Replace 'OTHER_USER' with the username to grant privileges to.
  -- DBMS_SCHEDULER.GRANT_PRIVILEGE (
  --  privilege   => 'EXECUTE',
  --  grantee     => 'OCI_FOCUS_REPORTS',
  --  grantor     => 'ADMIN',  --  The owner of the job.  If created in another schema, change this.
  --  object_name => 'GATHER_OCI_FOCUS_REPORTS_STATS'
  --);


  -- Optional:  Set job class attributes.  Useful for resource management.
  -- DBMS_SCHEDULER.SET_JOB_CLASS_ATTRIBUTE (
  --   job_class_name  => 'YOUR_JOB_CLASS',
  --   attribute       => 'RESOURCE_CONSUMER_GROUP',
  --   value           => 'MY_RESOURCE_GROUP'
  -- );

  -- Optional:  Create a job class.
  -- DBMS_SCHEDULER.CREATE_JOB_CLASS (
  --    job_class_name          =>  'YOUR_JOB_CLASS',
  --    resource_consumer_group =>  'MY_RESOURCE_GROUP',
  --    service                 =>  'your_service_name',
  --    logging_level           =>  DBMS_SCHEDULER.LOGGING_FULL
  -- );


  COMMIT;
  DBMS_OUTPUT.PUT_LINE('Scheduler job "GATHER_OCI_FOCUS_REPORTS_STATS" created and enabled.');

EXCEPTION
  WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('Error creating scheduler job: ' || SQLERRM);
    ROLLBACK;
END;