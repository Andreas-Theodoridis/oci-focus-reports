prompt --application/set_environment
set define off verify off feedback off
whenever sqlerror exit sql.sqlcode rollback
--------------------------------------------------------------------------------
--
-- Oracle APEX export file
--
-- You should run this script using a SQL client connected to the database as
-- the owner (parsing schema) of the application or as a database user with the
-- APEX_ADMINISTRATOR_ROLE role.
--
-- This export file has been automatically generated. Modifying this file is not
-- supported by Oracle and can lead to unexpected application and/or instance
-- behavior now or in the future.
--
-- NOTE: Calls to apex_application_install override the defaults below.
--
--------------------------------------------------------------------------------
begin
wwv_flow_imp.import_begin (
 p_version_yyyy_mm_dd=>'2024.11.30'
,p_default_workspace_id=>7775527647407456
);
end;
/
prompt  WORKSPACE 7775527647407456
--
-- Workspace, User Group, User, and Team Development Export:
--   Date and Time:   15:08 Wednesday July 2, 2025
--   Exported By:     ADMIN
--   Export Type:     Workspace Export
--   Version:         24.2.5
--   Instance ID:     7778856926809433
--
-- Import:
--   Using Instance Administration / Manage Workspaces
--   or
--   Using SQL*Plus as the Oracle user APEX_240200
 
begin
    wwv_flow_imp.set_security_group_id(p_security_group_id=>7775527647407456);
end;
/
----------------
-- W O R K S P A C E
-- Creating a workspace will not create database schemas or objects.
-- This API creates only the meta data for this APEX workspace
prompt  Creating workspace OCI_FOCUS_REPORTS...
begin
wwv_flow_fnd_user_api.create_company (
  p_id => 7775835068407500
 ,p_provisioning_company_id => 7775527647407456
 ,p_short_name => 'OCI_FOCUS_REPORTS'
 ,p_display_name => 'OCI_FOCUS_REPORTS'
 ,p_first_schema_provisioned => 'OCI_FOCUS_REPORTS'
 ,p_company_schemas => 'OCI_FOCUS_REPORTS'
 ,p_account_status => 'ASSIGNED'
 ,p_allow_plsql_editing => 'Y'
 ,p_allow_app_building_yn => 'Y'
 ,p_allow_packaged_app_ins_yn => 'Y'
 ,p_allow_sql_workshop_yn => 'Y'
 ,p_allow_team_development_yn => 'Y'
 ,p_allow_to_be_purged_yn => 'Y'
 ,p_allow_restful_services_yn => 'Y'
 ,p_source_identifier => 'OCI_FOCU'
 ,p_webservice_logging_yn => 'Y'
 ,p_path_prefix => 'OCI_FOCUS_REPORTS'
 ,p_files_version => 1
 ,p_is_extension_yn => 'N'
 ,p_env_banner_yn => 'N'
 ,p_env_banner_pos => 'LEFT'
);
end;
/
----------------
-- G R O U P S
--
prompt  Creating Groups...
begin
wwv_flow_fnd_user_api.create_user_group (
  p_id => 1405898031030452,
  p_GROUP_NAME => 'OAuth2 Client Developer',
  p_SECURITY_GROUP_ID => 10,
  p_GROUP_DESC => 'Users authorized to register OAuth2 Client Applications');
end;
/
begin
wwv_flow_fnd_user_api.create_user_group (
  p_id => 1405745204030452,
  p_GROUP_NAME => 'RESTful Services',
  p_SECURITY_GROUP_ID => 10,
  p_GROUP_DESC => 'Users authorized to use RESTful Services with this workspace');
end;
/
begin
wwv_flow_fnd_user_api.create_user_group (
  p_id => 1405683304030451,
  p_GROUP_NAME => 'SQL Developer',
  p_SECURITY_GROUP_ID => 10,
  p_GROUP_DESC => 'Users authorized to use SQL Developer with this workspace');
end;
/
begin
wwv_flow_fnd_user_api.create_user_group (
  p_id => 8095228254626798,
  p_GROUP_NAME => 'Administrators',
  p_SECURITY_GROUP_ID => 7775527647407456,
  p_GROUP_DESC => '');
end;
/
begin
wwv_flow_fnd_user_api.create_user_group (
  p_id => 8095388461627708,
  p_GROUP_NAME => 'Contributors',
  p_SECURITY_GROUP_ID => 7775527647407456,
  p_GROUP_DESC => '');
end;
/
prompt  Creating group grants...
begin
wwv_flow_fnd_user_api.set_group_group_grants (
  p_group_id => 8095228254626798
, p_granted_group_ids => wwv_flow_t_number(1405683304030451
                       , 1405745204030452
                       , 1405898031030452
));
end;
/
----------------
-- U S E R S
-- User repository for use with APEX cookie-based authentication.
--
prompt  Creating Users...
begin
wwv_flow_fnd_user_api.create_fnd_user (
  p_user_id                      => '8403525156288561',
  p_user_name                    => 'OVADMIN',
  p_first_name                   => '',
  p_last_name                    => '',
  p_description                  => '',
  p_email_address                => 'admin@obv.local',
  p_web_password                 => 'E08918543F8DCE62EC441F278D14541CABE9C707B8DA652BADCBC6F0E6C01567DCF3B3030E7C364CDA19240E64FA500666C88DF396EFA74A09D167670D232C87',
  p_web_password_format          => '5;5;10000',
  p_group_ids                    => '8095228254626798:',
  p_developer_privs              => 'ADMIN:CREATE:DATA_LOADER:EDIT:HELP:MONITOR:SQL',
  p_default_schema               => 'OCI_FOCUS_REPORTS',
  p_account_locked               => 'N',
  p_account_expiry               => to_date('202507020000','YYYYMMDDHH24MI'),
  p_failed_access_attempts       => 0,
  p_change_password_on_first_use => 'N',
  p_first_password_use_occurred  => 'N',
  p_allow_app_building_yn        => 'Y',
  p_allow_sql_workshop_yn        => 'Y',
  p_allow_team_development_yn    => 'Y',
  p_allow_access_to_schemas      => '');
end;
/
begin
wwv_flow_fnd_user_api.create_fnd_user (
  p_user_id                      => '63531805767603756',
  p_user_name                    => 'OCI_FOCUS_REPORTS',
  p_first_name                   => '',
  p_last_name                    => '',
  p_description                  => '',
  p_email_address                => 'ofcr@ofcr.internal.local',
  p_web_password                 => 'FE96E53689314449408C35D8D8C694814558A43846A3686B01C03527961798EA39CECBE6D9B8073649840921D0EA952CECDB9A26FC86F05993E4B138CECBA3B7',
  p_web_password_format          => '5;5;10000',
  p_group_ids                    => '',
  p_developer_privs              => 'ADMIN:CREATE:DATA_LOADER:EDIT:HELP:MONITOR:SQL',
  p_default_schema               => 'OCI_FOCUS_REPORTS',
  p_account_locked               => 'N',
  p_account_expiry               => to_date('202506141655','YYYYMMDDHH24MI'),
  p_failed_access_attempts       => 0,
  p_change_password_on_first_use => 'N',
  p_first_password_use_occurred  => 'Y',
  p_allow_app_building_yn        => 'Y',
  p_allow_sql_workshop_yn        => 'Y',
  p_allow_team_development_yn    => 'Y',
  p_allow_access_to_schemas      => '');
end;
/
---------------------------
-- D G  B L U E P R I N T S
-- Creating Data Generator Blueprints...
begin
wwv_flow_imp.import_end(p_auto_install_sup_obj => nvl(wwv_flow_application_install.get_auto_install_sup_obj, false)
);
commit;
end;
/
set verify on feedback on define on
prompt  ...done
