
  CREATE TABLE "OCI_FOCUS_REPORTS"."FILTER_VALUES_MV"
   (	"SUBACCOUNTNAME" VARCHAR2(4000 BYTE),
	"BILLINGACCOUNTID" NUMBER,
	"REGION" VARCHAR2(4000 BYTE),
	"OCI_COMPARTMENTID" VARCHAR2(4000 BYTE),
	"SERVICECATEGORY" VARCHAR2(4000 BYTE),
	"SERVICENAME" VARCHAR2(4000 BYTE),
	"CHARGEDESCRIPTION" VARCHAR2(4000 BYTE),
	"RESOURCETYPE" VARCHAR2(4000 BYTE),
	"RESOURCEID" VARCHAR2(4000 BYTE),
	"RESOURCENAME" VARCHAR2(1000 BYTE)
   ) ;


  CREATE TABLE "OCI_FOCUS_REPORTS"."CREDIT_USAGE_AGG"
   (	"BILLINGACCOUNTID" VARCHAR2(100 BYTE),
	"CHARGEPERIODEND" DATE,
	"BILLEDCOST" NUMBER,
	"HOURLY_COST" NUMBER,
	"INSERTED_AT" DATE DEFAULT SYSDATE
   ) ;


  CREATE TABLE "OCI_FOCUS_REPORTS"."PAGE1_CONS_WRKLD_WEEK_CHART_DATA"
   (	"WORKLOAD_NAME" VARCHAR2(400 BYTE),
	"WEEK_START" DATE,
	"COST" NUMBER,
	"LAST_REFRESH" DATE
   ) ;
ALTER TABLE "OCI_FOCUS_REPORTS"."PAGE1_CONS_WRKLD_WEEK_CHART_DATA" ADD PRIMARY K
EY ("WORKLOAD_NAME", "WEEK_START")
  USING INDEX  ENABLE;


  CREATE TABLE "OCI_FOCUS_REPORTS"."PAGE1_CONS_WRKLD_MONTH_CHART_DATA"
   (	"WORKLOAD_NAME" VARCHAR2(400 BYTE),
	"MONTH" DATE,
	"COST" NUMBER,
	"LAST_REFRESH" DATE
   ) ;
ALTER TABLE "OCI_FOCUS_REPORTS"."PAGE1_CONS_WRKLD_MONTH_CHART_DATA" ADD PRIMARY
KEY ("WORKLOAD_NAME", "MONTH")
  USING INDEX  ENABLE;


  CREATE TABLE "OCI_FOCUS_REPORTS"."COST_USAGE_TIMESERIES"
   (	"DATE_BUCKET" DATE,
	"GRANULARITY" VARCHAR2(10 BYTE),
	"BILLINGACCOUNTID" VARCHAR2(200 BYTE),
	"SUBACCOUNTNAME" VARCHAR2(200 BYTE),
	"INVOICEISSUER" VARCHAR2(200 BYTE),
	"REGION" VARCHAR2(100 BYTE),
	"BILLINGCURRENCY" VARCHAR2(20 BYTE),
	"SERVICECATEGORY" VARCHAR2(200 BYTE),
	"SERVICENAME" VARCHAR2(200 BYTE),
	"CHARGEDESCRIPTION" VARCHAR2(400 BYTE),
	"RESOURCETYPE" VARCHAR2(200 BYTE),
	"RESOURCEID" VARCHAR2(400 BYTE),
	"SKUID" VARCHAR2(200 BYTE),
	"PRICINGUNIT" VARCHAR2(100 BYTE),
	"OCI_COMPARTMENTID" VARCHAR2(400 BYTE),
	"OCI_COMPARTMENTNAME" VARCHAR2(400 BYTE),
	"USAGEUNIT" VARCHAR2(100 BYTE),
	"COST" NUMBER(20,6),
	"USAGE" NUMBER(20,6),
	"LAST_REFRESH" DATE
   ) ;


  CREATE TABLE "OCI_FOCUS_REPORTS"."PAGE3_COST_USAGE_TIMESERIES"
   (	"DATE_BUCKET" DATE,
	"GRANULARITY" VARCHAR2(10 BYTE),
	"BILLINGACCOUNTID" VARCHAR2(200 BYTE),
	"SUBACCOUNTNAME" VARCHAR2(200 BYTE),
	"INVOICEISSUER" VARCHAR2(200 BYTE),
	"REGION" VARCHAR2(100 BYTE),
	"BILLINGCURRENCY" VARCHAR2(20 BYTE),
	"SERVICECATEGORY" VARCHAR2(200 BYTE),
	"SERVICENAME" VARCHAR2(200 BYTE),
	"CHARGEDESCRIPTION" VARCHAR2(400 BYTE),
	"RESOURCETYPE" VARCHAR2(200 BYTE),
	"RESOURCEID" VARCHAR2(400 BYTE),
	"SKUID" VARCHAR2(200 BYTE),
	"PRICINGUNIT" VARCHAR2(100 BYTE),
	"OCI_COMPARTMENTID" VARCHAR2(400 BYTE),
	"OCI_COMPARTMENTNAME" VARCHAR2(400 BYTE),
	"USAGEUNIT" VARCHAR2(100 BYTE),
	"COST" NUMBER(20,6),
	"USAGE" NUMBER(20,6),
	"LAST_REFRESH" DATE
   ) ;


  CREATE TABLE "OCI_FOCUS_REPORTS"."OCI_AVAILABILITY_METRICS_PY"
   (	"RESOURCEDISPLAYNAME" VARCHAR2(64 BYTE),
	"TIMESTAMP" TIMESTAMP (6),
	"NAMESPACE" VARCHAR2(64 BYTE),
	"COMPARTMENT_ID" VARCHAR2(256 BYTE),
	"VALUE" NUMBER,
	"METRIC_NAME" VARCHAR2(128 BYTE)
   )
  PARTITION BY RANGE ("TIMESTAMP") INTERVAL (NUMTOYMINTERVAL(1, 'MONTH'))
 (PARTITION "OCI_AVAILABILITY_METRICS_PY_BEFORE_2022"  VALUES LESS THAN (TIMESTA
MP' 2022-01-01 00:00:00') ) ;


  CREATE TABLE "OCI_FOCUS_REPORTS"."OCI_EXA_MAINTENANCE_PY"
   (	"ID" VARCHAR2(1000 BYTE),
	"COMPARTMENT_ID" VARCHAR2(1000 BYTE),
	"CURRENT_CUSTOM_ACTION_TIMEOUT_IN_MINS" NUMBER,
	"CURRENT_PATCHING_COMPONENT" VARCHAR2(1000 BYTE),
	"CUSTOM_ACTION_TIMEOUT_IN_MINS" NUMBER,
	"DATABASE_SOFTWARE_IMAGE_ID" VARCHAR2(1000 BYTE),
	"DESCRIPTION" VARCHAR2(10000 BYTE),
	"DISPLAY_NAME" VARCHAR2(500 BYTE),
	"ESTIMATED_DB_SERVER_PATCHING_TIME" NUMBER,
	"ESTIMATED_NETWORK_SWITCHES_PATCHING_TIME" NUMBER,
	"ESTIMATED_STORAGE_SERVER_PATCHING_TIME" NUMBER,
	"TOTAL_ESTIMATED_PATCHING_TIME" NUMBER,
	"IS_CUSTOM_ACTION_TIMEOUT_ENABLED" VARCHAR2(10 BYTE),
	"IS_DST_FILE_UPDATE_ENABLED" VARCHAR2(10 BYTE),
	"IS_MAINTENANCE_RUN_GRANULAR" VARCHAR2(10 BYTE),
	"LIFECYCLE_DETAILS" VARCHAR2(10000 BYTE),
	"LIFECYCLE_STATE" VARCHAR2(50 BYTE),
	"MAINTENANCE_SUBTYPE" VARCHAR2(1000 BYTE),
	"MAINTENANCE_TYPE" VARCHAR2(1000 BYTE),
	"PATCH_FAILURE_COUNT" NUMBER,
	"PATCH_ID" VARCHAR2(50 BYTE),
	"PATCHING_END_TIME" TIMESTAMP (6),
	"PATCHING_MODE" VARCHAR2(50 BYTE),
	"PATCHING_START_TIME" TIMESTAMP (6),
	"PATCHING_STATUS" VARCHAR2(50 BYTE),
	"PEER_MAINTENANCE_RUN_ID" VARCHAR2(1000 BYTE),
	"PEER_MAINTENANCE_RUN_IDS" CLOB,
	"TARGET_DB_SERVER_VERSION" VARCHAR2(1000 BYTE),
	"TARGET_RESOURCE_ID" VARCHAR2(200 BYTE),
	"TARGET_RESOURCE_TYPE" VARCHAR2(1000 BYTE),
	"TARGET_STORAGE_SERVER_VERSION" VARCHAR2(1000 BYTE),
	"TIME_ENDED" TIMESTAMP (6),
	"TIME_SCHEDULED" TIMESTAMP (6),
	"TIME_STARTED" TIMESTAMP (6),
	"TOTAL_TIME_TAKEN_IN_MINS" NUMBER
   ) ;


  CREATE TABLE "OCI_FOCUS_REPORTS"."OCI_SUBSCRIPTIONS_PY"
   (	"SUBSCRIPTION_ID" VARCHAR2(100 BYTE),
	"ISO_CODE" VARCHAR2(10 BYTE),
	"NAME" VARCHAR2(100 BYTE),
	"STD_PRECISION" NUMBER,
	"SERVICE_NAME" VARCHAR2(100 BYTE),
	"STATUS" VARCHAR2(50 BYTE),
	"AVAILABLE_AMOUNT" VARCHAR2(100 BYTE),
	"BOOKING_OPTY_NUMBER" VARCHAR2(100 BYTE),
	"COMMITMENT_SERVICES" CLOB,
	"CSI" VARCHAR2(100 BYTE),
	"DATA_CENTER_REGION" VARCHAR2(100 BYTE),
	"FUNDED_ALLOCATION_VALUE" VARCHAR2(100 BYTE),
	"ID" VARCHAR2(100 BYTE),
	"IS_INTENT_TO_PAY" VARCHAR2(10 BYTE),
	"NET_UNIT_PRICE" VARCHAR2(100 BYTE),
	"OPERATION_TYPE" VARCHAR2(100 BYTE),
	"ORDER_NUMBER" VARCHAR2(100 BYTE),
	"ORIGINAL_PROMO_AMOUNT" VARCHAR2(100 BYTE),
	"PARTNER_TRANSACTION_TYPE" VARCHAR2(100 BYTE),
	"PRICING_MODEL" VARCHAR2(100 BYTE),
	"PRODUCT_NAME" VARCHAR2(200 BYTE),
	"PRODUCT_PART_NUMBER" VARCHAR2(100 BYTE),
	"PRODUCT_PROVISIONING_GROUP" VARCHAR2(100 BYTE),
	"PRODUCT_UNIT_OF_MEASURE" VARCHAR2(100 BYTE),
	"PROGRAM_TYPE" VARCHAR2(100 BYTE),
	"PROMO_TYPE" VARCHAR2(100 BYTE),
	"QUANTITY" VARCHAR2(100 BYTE),
	"SUBSTATUS" VARCHAR2(100 BYTE),
	"TIME_END" VARCHAR2(50 BYTE),
	"TIME_START" VARCHAR2(50 BYTE),
	"TOTAL_VALUE" VARCHAR2(100 BYTE),
	"USED_AMOUNT" VARCHAR2(100 BYTE)
   ) ;


  CREATE TABLE "OCI_FOCUS_REPORTS"."OCI_WORKLOADS"
   (	"WORKLOAD_NAME" VARCHAR2(100 BYTE) NOT NULL ENABLE,
	"VALUE" CLOB NOT NULL ENABLE
   ) ;
ALTER TABLE "OCI_FOCUS_REPORTS"."OCI_WORKLOADS" ADD CONSTRAINT "OCI_WORKLOADS_PK
" PRIMARY KEY ("WORKLOAD_NAME")
  USING INDEX  ENABLE;


  CREATE TABLE "OCI_FOCUS_REPORTS"."AI_USER_SESSIONS"
   (	"USER_NAME" VARCHAR2(255 BYTE),
	"SESSION_ID" VARCHAR2(4000 BYTE),
	"CREATED_ON" TIMESTAMP (6) DEFAULT SYSTIMESTAMP
   ) ;
ALTER TABLE "OCI_FOCUS_REPORTS"."AI_USER_SESSIONS" ADD PRIMARY KEY ("USER_NAME")

  USING INDEX  ENABLE;


  CREATE TABLE "OCI_FOCUS_REPORTS"."OCI_COMPARTMENTS_PY"
   (	"COMPARTMENT_ID" VARCHAR2(4000 BYTE),
	"NAME" VARCHAR2(4000 BYTE),
	"DESCRIPTION" VARCHAR2(4000 BYTE),
	"LIFECYCLE_STATE" VARCHAR2(4000 BYTE),
	"TIME_CREATED" VARCHAR2(4000 BYTE),
	"PARENT_ID" VARCHAR2(4000 BYTE),
	"PARENT" VARCHAR2(4000 BYTE),
	"PATH" VARCHAR2(4000 BYTE),
	"TENANCY_ID" VARCHAR2(2000 BYTE)
   ) ;


  CREATE TABLE "OCI_FOCUS_REPORTS"."OCI_RESOURCES_PY"
   (	"DISPLAY_NAME" VARCHAR2(1000 BYTE),
	"IDENTIFIER" VARCHAR2(1000 BYTE),
	"REGION" VARCHAR2(60 BYTE)
   ) ;


  CREATE TABLE "OCI_FOCUS_REPORTS"."OCI_SUBSCRIPTION_DETAILS"
   (	"SUBSCRIPTION_ID" NUMBER,
	"START_DATE" DATE,
	"END_DATE" DATE,
	"COMMITED_CREDITS" NUMBER,
	"CREDITS_CONSUMED" VARCHAR2(20 BYTE),
	"CREDITS_CONSUMED_DATE" DATE,
	"ORDER_NAME" VARCHAR2(128 BYTE),
	"CURRENCY" VARCHAR2(20 BYTE),
	"ORDER_ID" NUMBER
   ) ;


  CREATE TABLE "OCI_FOCUS_REPORTS"."AI_CHAT_LOG"
   (	"ID" NUMBER GENERATED BY DEFAULT ON NULL AS IDENTITY MINVALUE 1 MAXVALUE 99
99999999999999999999999999 INCREMENT BY 1 START WITH 1 CACHE 20 NOORDER  NOCYCLE
  NOKEEP  NOSCALE  NOT NULL ENABLE,
	"CHAT_ID" NUMBER NOT NULL ENABLE,
	"APP_USER" VARCHAR2(255 BYTE),
	"SESSION_ID" VARCHAR2(255 BYTE),
	"USER_MESSAGE" CLOB,
	"GENERATED_SQL" CLOB,
	"EXECUTION_DATA" CLOB,
	"RAW_RESPONSE" CLOB,
	"SUMMARY_TEXT" CLOB,
	"REASONED_MESSAGE" CLOB,
	"CREATED_AT" TIMESTAMP (6) DEFAULT SYSTIMESTAMP
   ) ;
ALTER TABLE "OCI_FOCUS_REPORTS"."AI_CHAT_LOG" ADD PRIMARY KEY ("ID")
  USING INDEX  ENABLE;


  CREATE TABLE "OCI_FOCUS_REPORTS"."AI_CHAT_LOG_REASONING"
   (	"ID" NUMBER GENERATED BY DEFAULT ON NULL AS IDENTITY MINVALUE 1 MAXVALUE 99
99999999999999999999999999 INCREMENT BY 1 START WITH 1 CACHE 20 NOORDER  NOCYCLE
  NOKEEP  NOSCALE  NOT NULL ENABLE,
	"CHAT_ID" NUMBER NOT NULL ENABLE,
	"LOG_ID" NUMBER,
	"INPUT_MESSAGE" CLOB,
	"REPHRASED_OUTPUT" CLOB,
	"ATTEMPT_NUMBER" NUMBER,
	"APP_USER" VARCHAR2(255 BYTE),
	"CREATED_AT" TIMESTAMP (6) DEFAULT SYSTIMESTAMP
   ) ;
ALTER TABLE "OCI_FOCUS_REPORTS"."AI_CHAT_LOG_REASONING" ADD PRIMARY KEY ("ID")
  USING INDEX  ENABLE;


  CREATE TABLE "OCI_FOCUS_REPORTS"."RATECARD_MV"
   (	"CHARGEDESCRIPTION" VARCHAR2(4000 BYTE),
	"PRICINGUNIT" VARCHAR2(4000 BYTE),
	"SKUID" VARCHAR2(4000 BYTE),
	"ACTUALUNITPRICE" NUMBER,
	"LISTUNITPRICE" NUMBER
   ) ;


  CREATE TABLE "OCI_FOCUS_REPORTS"."DBTOOLS$EXECUTION_HISTORY"
   (	"ID" NUMBER NOT NULL ENABLE,
	"HASH" CLOB,
	"CREATED_BY" VARCHAR2(255 BYTE),
	"CREATED_ON" TIMESTAMP (6) WITH TIME ZONE,
	"UPDATED_BY" VARCHAR2(255 BYTE),
	"UPDATED_ON" TIMESTAMP (6) WITH TIME ZONE,
	"STATEMENT" CLOB,
	"TIMES" NUMBER
   ) ;
ALTER TABLE "OCI_FOCUS_REPORTS"."DBTOOLS$EXECUTION_HISTORY" ADD CONSTRAINT "DBTO
OLS$EXECUTION_HISTORY_PK" PRIMARY KEY ("ID")
  USING INDEX  ENABLE;


  CREATE TABLE "OCI_FOCUS_REPORTS"."FOCUS_REPORTS_PY"
   (	"AVAILABILITYZONE" VARCHAR2(4000 BYTE),
	"BILLEDCOST" NUMBER,
	"BILLINGACCOUNTID" NUMBER,
	"BILLINGACCOUNTNAME" VARCHAR2(32767 BYTE),
	"BILLINGCURRENCY" VARCHAR2(4000 BYTE),
	"BILLINGPERIODEND" TIMESTAMP (6),
	"BILLINGPERIODSTART" TIMESTAMP (6),
	"CHARGECATEGORY" VARCHAR2(4000 BYTE),
	"CHARGEDESCRIPTION" VARCHAR2(4000 BYTE),
	"CHARGEFREQUENCY" VARCHAR2(32767 BYTE),
	"CHARGEPERIODEND" TIMESTAMP (6),
	"CHARGEPERIODSTART" TIMESTAMP (6),
	"CHARGESUBCATEGORY" VARCHAR2(32767 BYTE),
	"COMMITMENTDISCOUNTCATEGORY" VARCHAR2(32767 BYTE),
	"COMMITMENTDISCOUNTID" VARCHAR2(32767 BYTE),
	"COMMITMENTDISCOUNTNAME" VARCHAR2(32767 BYTE),
	"COMMITMENTDISCOUNTTYPE" VARCHAR2(32767 BYTE),
	"EFFECTIVECOST" NUMBER,
	"INVOICEISSUER" VARCHAR2(4000 BYTE),
	"LISTCOST" NUMBER,
	"LISTUNITPRICE" NUMBER,
	"PRICINGCATEGORY" VARCHAR2(32767 BYTE),
	"PRICINGQUANTITY" NUMBER,
	"PRICINGUNIT" VARCHAR2(4000 BYTE),
	"PROVIDER" VARCHAR2(4000 BYTE),
	"PUBLISHER" VARCHAR2(4000 BYTE),
	"REGION" VARCHAR2(4000 BYTE),
	"RESOURCEID" VARCHAR2(4000 BYTE),
	"RESOURCENAME" VARCHAR2(32767 BYTE),
	"RESOURCETYPE" VARCHAR2(4000 BYTE),
	"SERVICECATEGORY" VARCHAR2(4000 BYTE),
	"SERVICENAME" VARCHAR2(4000 BYTE),
	"SKUID" VARCHAR2(4000 BYTE),
	"SKUPRICEID" VARCHAR2(32767 BYTE),
	"SUBACCOUNTID" VARCHAR2(4000 BYTE),
	"SUBACCOUNTNAME" VARCHAR2(4000 BYTE),
	"TAGS" CLOB,
	"USAGEQUANTITY" NUMBER,
	"USAGEUNIT" VARCHAR2(4000 BYTE),
	"OCI_REFERENCENUMBER" VARCHAR2(4000 BYTE),
	"OCI_COMPARTMENTID" VARCHAR2(4000 BYTE),
	"OCI_COMPARTMENTNAME" VARCHAR2(4000 BYTE),
	"OCI_OVERAGEFLAG" VARCHAR2(4000 BYTE),
	"OCI_UNITPRICEOVERAGE" VARCHAR2(32767 BYTE),
	"OCI_BILLEDQUANTITYOVERAGE" VARCHAR2(32767 BYTE),
	"OCI_COSTOVERAGE" VARCHAR2(32767 BYTE),
	"OCI_ATTRIBUTEDUSAGE" NUMBER,
	"OCI_ATTRIBUTEDCOST" NUMBER,
	"OCI_BACKREFERENCENUMBER" VARCHAR2(4000 BYTE)
   )
  PARTITION BY RANGE ("CHARGEPERIODSTART") INTERVAL (NUMTOYMINTERVAL(1, 'MONTH')
)
 (PARTITION "P_BEFORE_2024"  VALUES LESS THAN (TIMESTAMP' 2024-01-01 00:00:00')
) ;


  CREATE INDEX "OCI_FOCUS_REPORTS"."IDX_CREDIT_AGG_BILLING" ON "OCI_FOCUS_REPORT
S"."CREDIT_USAGE_AGG" ("BILLINGACCOUNTID", "CHARGEPERIODEND")
  ;


  CREATE INDEX "OCI_FOCUS_REPORTS"."IDX_FOCUS_REPORTS_OCI_REF" ON "OCI_FOCUS_REP
ORTS"."FOCUS_REPORTS_PY" ("OCI_REFERENCENUMBER")
  ;


  CREATE INDEX "OCI_FOCUS_REPORTS"."IDX_FRP_CPE" ON "OCI_FOCUS_REPORTS"."FOCUS_R
EPORTS_PY" ("CHARGEPERIODEND")
  ;


  CREATE INDEX "OCI_FOCUS_REPORTS"."IDX_FRP_BAID_CPE" ON "OCI_FOCUS_REPORTS"."FO
CUS_REPORTS_PY" ("BILLINGACCOUNTID", "CHARGEPERIODEND")
  ;


  CREATE UNIQUE INDEX "OCI_FOCUS_REPORTS"."OCI_WORKLOADS_PK" ON "OCI_FOCUS_REPOR
TS"."OCI_WORKLOADS" ("WORKLOAD_NAME")
  ;


  CREATE BITMAP INDEX "OCI_FOCUS_REPORTS"."IDX_OCI_CC" ON "OCI_FOCUS_REPORTS"."O
CI_SUBSCRIPTION_DETAILS" ("CREDITS_CONSUMED")
  ;


  CREATE BITMAP INDEX "OCI_FOCUS_REPORTS"."IDX_OCI_CURRENCY" ON "OCI_FOCUS_REPOR
TS"."OCI_SUBSCRIPTION_DETAILS" ("CURRENCY")
  ;


  CREATE UNIQUE INDEX "OCI_FOCUS_REPORTS"."DBTOOLS$EXECUTION_HISTORY_PK" ON "OCI
_FOCUS_REPORTS"."DBTOOLS$EXECUTION_HISTORY" ("ID")
  ;


Error starting at line : 30 in command -
SELECT DBMS_METADATA.GET_DDL('SEQUENCE', sequence_name, user) FROM user_sequences
Error at Command Line : 30 Column : 8
Error report -
SQL Error: ORA-31603: object "ISEQ$$_110954" of type SEQUENCE not found in schema "OCI_FOCUS_REPORTS"
ORA-06512: at "SYS.DBMS_METADATA", line 6775
ORA-06512: at "SYS.DBMS_SYS_ERROR", line 150
ORA-06512: at "SYS.DBMS_METADATA", line 6762
ORA-06512: at "SYS.DBMS_METADATA", line 9739
ORA-06512: at line 1

https://docs.oracle.com/error-help/db/ora-31603/31603. 00000 -  "object \"%s\" of type %s not found in schema \"%s\""
*Cause:    The specified object was not found in the database.
*Action:   Correct the object specification and try the call again.

More Details :
https://docs.oracle.com/error-help/db/ora-31603/
https://docs.oracle.com/error-help/db/ora-06512/

  CREATE OR REPLACE FORCE EDITIONABLE VIEW "OCI_FOCUS_REPORTS"."EA_REMAINING_CRE
DITS_PY_V" ("REMAINING_CREDITS") AS
  select (select sum(s.COMMITED_CREDITS) FROM OCI_SUBSCRIPTION_DETAILS s where O
RDER_NAME NOT IN ('DB@Azure', 'ExaCC'))
- (select sum(c.BILLEDCOST) from FOCUS_REPORTS_PY c
    where TRUNC(CHARGEPERIODEND, 'HH') <= TO_TIMESTAMP_TZ('2024-12-29T23:00Z', '
YYYY-MM-DD"T"HH24:MI"Z"')
    AND  TRUNC(CHARGEPERIODSTART, 'HH') >= TO_TIMESTAMP_TZ('2024-09-21T00:00Z',
'YYYY-MM-DD"T"HH24:MI"Z"')
    AND BILLINGACCOUNTID='9379274') AS REMAINING_CREDITS
FROM DUAL;


  CREATE OR REPLACE FORCE EDITIONABLE VIEW "OCI_FOCUS_REPORTS"."EXACC_REMAINING_
CREDITS_PY_V" ("REMAINING_CREDITS") AS
  select (select sum(s.COMMITED_CREDITS) FROM OCI_SUBSCRIPTION_DETAILS s where O
RDER_NAME NOT IN ('DB@Azure','EA'))
- (select sum(c.BILLEDCOST) from FOCUS_REPORTS_PY c
    where TRUNC(CHARGEPERIODEND, 'HH') >= TO_TIMESTAMP_TZ('2024-12-29T23:00Z', '
YYYY-MM-DD"T"HH24:MI"Z"')
    AND BILLINGACCOUNTID='9379274') AS REMAINING_CREDITS
FROM DUAL;


  CREATE OR REPLACE EDITIONABLE PROCEDURE "OCI_FOCUS_REPORTS"."REFRESH_CREDIT_US
AGE_AGG_PROC" AS
BEGIN
  EXECUTE IMMEDIATE 'TRUNCATE TABLE CREDIT_USAGE_AGG';

  INSERT INTO CREDIT_USAGE_AGG (BILLINGACCOUNTID, CHARGEPERIODEND, BILLEDCOST,
HOURLY_COST)
  SELECT
    BILLINGACCOUNTID,
    TRUNC(CHARGEPERIODEND, 'HH') AS CHARGEPERIODEND,
    SUM(BILLEDCOST) AS BILLEDCOST,
    SUM(BILLEDCOST) / 1 AS HOURLY_COST
  FROM FOCUS_REPORTS_PY
  WHERE CHARGEPERIODEND >= SYSDATE - 30  -- or -90 for 3 months of history
  GROUP BY BILLINGACCOUNTID, TRUNC(CHARGEPERIODEND, 'HH');

  COMMIT;
END;
/


  CREATE OR REPLACE EDITIONABLE PROCEDURE "OCI_FOCUS_REPORTS"."OV_AI_AGENT_PROC"
 (
    p_user_message     IN VARCHAR2,
    p_sql_agent_id     IN VARCHAR2,
    p_chat_id          IN NUMBER,
    p_app_user         IN VARCHAR2,
    p_app_session      IN VARCHAR2,
    p_region           IN VARCHAR2,
    p_compartment_id   IN VARCHAR2,
    p_row_id           OUT ai_chat_log.id%TYPE,
    p_final_sql        OUT CLOB,
    p_final_response   OUT CLOB,
    p_final_aimessage  OUT CLOB
) AS
    -- Variables reused across attempts
    v_attempt              NUMBER := 0;
    v_max_attempts         CONSTANT NUMBER := 5;
    v_last_failed          VARCHAR2(1) := 'Y';
    v_reasoned_message     CLOB;
    v_reasoning_row_id     NUMBER;

    -- AI agent vars
    v_response_sql         CLOB;
    v_response             CLOB;
    v_aimessage            CLOB;
    v_log_row_id           ai_chat_log.id%TYPE;

    -- Reasoning vars
    l_input_text           VARCHAR2(4000);
    l_prompt               VARCHAR2(4000);
    l_payload              CLOB;
    l_reasoning_response   CLOB;
    l_response_struct      DBMS_CLOUD_TYPES.resp;
    l_resp_obj             JSON_OBJECT_T;
    l_result_text          VARCHAR2(4000);

    -- Summary vars
    v_summary_text         CLOB;
    v_summary_prompt       VARCHAR2(4000);

    -- JSON and execution vars
    l_json_payload         JSON_OBJECT_T;
    l_outer_obj            JSON_OBJECT_T;
    l_inner_obj            JSON_OBJECT_T;
    l_content_obj          JSON_OBJECT_T;
    l_inner_text           VARCHAR2(32767);
    l_exec_result          JSON_ARRAY_T;
    l_sql_body             VARCHAR2(32767);
    l_sql                  VARCHAR2(32767);
    l_cursor               INTEGER;
    l_desc_tab             DBMS_SQL.DESC_TAB;
    l_col_count            INTEGER;
    l_value                VARCHAR2(4000);
    l_has_data             BOOLEAN := FALSE;
    l_status               INTEGER;

    -- Endpoint URLs
    l_sql_endpoint         VARCHAR2(1000);
    l_reasoning_endpoint   VARCHAR2(1000);
BEGIN
    apex_debug.message('🔁 Starting ov_ai_agent_proc');

    l_sql_endpoint := 'https://agent-runtime.generativeai.' || LOWER(p_region)
||
                      '.oci.oraclecloud.com/20240531/agentEndpoints/' || p_sql_a
gent_id || '/actions/chat';
    l_reasoning_endpoint := 'https://inference.generativeai.' || LOWER(p_region)
 ||
                            '.oci.oraclecloud.com/20231130/actions/chat';

    apex_debug.message('🔗 Endpoints built. SQL: %s, Reasoning: %s', l_sql_endp
oint, l_reasoning_endpoint);

    LOOP
        v_attempt := v_attempt + 1;
        apex_debug.message('🔄 Attempt #%s', v_attempt);

        DECLARE
            l_input VARCHAR2(32767) := CASE WHEN v_attempt = 1 OR v_reasoned_mes
sage IS NULL THEN p_user_message ELSE v_reasoned_message END;
        BEGIN
            apex_debug.message('🧠 Input message: %s', l_input);

            -- Prepare SQL agent request
            l_json_payload := JSON_OBJECT_T.parse('{}');
            l_json_payload.put('userMessage', l_input);
            l_json_payload.put('context', JSON_OBJECT_T.parse('{}'));
            l_json_payload.put('isStream', FALSE);
            l_payload := l_json_payload.to_clob;

            apex_debug.message('📤 Sending SQL Agent pa');

            l_response_struct := DBMS_CLOUD.SEND_REQUEST(
                credential_name => 'OCI$RESOURCE_PRINCIPAL',
                uri             => l_sql_endpoint,
                method          => 'POST',
                headers         => JSON_OBJECT('Content-Type' VALUE 'application
/json'),
                body            => UTL_RAW.CAST_TO_RAW(l_payload)
            );

            v_response := DBMS_CLOUD.GET_RESPONSE_TEXT(l_response_struct);
            apex_debug.message('📥 SQL Agent raw response: %s', SUBSTR(v_respons
e, 1, 4000));

            IF v_response IS NULL THEN
                apex_debug.message('❌ SQL Agent returned NULL response.');
                v_last_failed := 'Y';
                CONTINUE;
            END IF;

            l_outer_obj := JSON_OBJECT_T.parse(v_response);
            IF NOT l_outer_obj.has('message') THEN
                apex_debug.message('❌ SQL Agent response missing "message"');
                v_last_failed := 'Y';
                CONTINUE;
            END IF;

            l_content_obj := l_outer_obj.get_Object('message').get_Object('cont
ent');
            IF l_content_obj IS NULL OR NOT l_content_obj.has('text') THEN
                apex_debug.message('❌ SQL Agent response missing "content.text"'
);
                v_last_failed := 'Y';
                CONTINUE;
            END IF;

            l_inner_text := l_content_obj.get_String('text');
            apex_debug.message('📦 SQL Agent inner text: %s', SUBSTR(l_inner_tex
t, 1, 1000));

            l_inner_obj := JSON_OBJECT_T.parse(l_inner_text);
            IF NOT l_inner_obj.has('generatedQuery') THEN
                apex_debug.message('❌ Missing "generatedQuery" in agent response
');
                v_last_failed := 'Y';
                CONTINUE;
            END IF;

            v_response_sql := l_inner_obj.get_String('generatedQuery');
            v_aimessage := CASE
                             WHEN l_inner_obj.has('executionResult') THEN l_inne
r_obj.get_Array('executionResult').to_string
                             ELSE '[]'
                           END;

            apex_debug.message('✅ SQL received: %s', SUBSTR(v_response_sql, 1,
1000));

            -- Validate SQL
            l_sql_body := RTRIM(v_response_sql, ';');
            l_sql := 'SELECT * FROM (' || l_sql_body || ') WHERE ROWNUM = 1';

            apex_debug.message('🔍 Validating SQL: %s', l_sql);

            l_cursor := DBMS_SQL.OPEN_CURSOR;
            DBMS_SQL.PARSE(l_cursor, l_sql, DBMS_SQL.NATIVE);
            DBMS_SQL.DESCRIBE_COLUMNS(l_cursor, l_col_count, l_desc_tab);

            FOR i IN 1 .. l_col_count LOOP
                DBMS_SQL.DEFINE_COLUMN(l_cursor, i, l_value, 4000);
            END LOOP;

            l_status := DBMS_SQL.EXECUTE(l_cursor);

            IF DBMS_SQL.FETCH_ROWS(l_cursor) > 0 THEN
                FOR i IN 1 .. l_col_count LOOP
                    DBMS_SQL.COLUMN_VALUE(l_cursor, i, l_value);
                    IF l_value IS NOT NULL THEN
                        l_has_data := TRUE;
                        EXIT;
                    END IF;
                END LOOP;
            END IF;

            DBMS_SQL.CLOSE_CURSOR(l_cursor);

            IF l_has_data THEN
                apex_debug.message('✅ SQL validation successful, logging...');

                v_last_failed := 'N';

                INSERT INTO ai_chat_log (
                    chat_id, app_user, session_id,
                    user_message, generated_sql, execution_data, raw_response
                ) VALUES (
                    p_chat_id, p_app_user, p_app_session,
                    l_input, v_response_sql, v_aimessage, v_response
                ) RETURNING id INTO v_log_row_id;

                UPDATE ai_chat_log_reasoning
                   SET log_id = v_log_row_id
                 WHERE chat_id = p_chat_id
                   AND log_id IS NULL;

                p_row_id := v_log_row_id;
                p_final_sql := v_response_sql;
             p_final_response := v_response;
                p_final_aimessage := v_aimessage;
                -- Generate Summary via GenAI using final AI message
                BEGIN
                    apex_debug.message('📝 Generating summary using DBMS_CLOUD a
nd GenAI');

                    v_summary_prompt := 'You are a helpful financial data analy
st. Format summaries clearly using these sections:' || CHR(10) ||
                                        '- Overview' || CHR(10) ||
                                        '- Details' || CHR(10) ||
                                        '- Totals' || CHR(10) ||
                                        '- Observations' || CHR(10) ||
                                        'Use plain text, line breaks, and bullet
 points.' || CHR(10) ||
                                        'Here is the data to analyze:';

                    l_input_text := v_summary_prompt || CHR(10) || CHR(10) || v
_aimessage;

                    apex_debug.message('📤 Summary Input Text: %s', SUBSTR(l_in
put_text, 1, 4000));

                    l_payload := '{
                      "compartmentId": "' || p_compartment_id || '",
                      "servingMode": {
                        "modelId": "cohere.command-a-03-2025",
                        "servingType": "ON_DEMAND"
                      },
                      "chatRequest": {
                        "message": "' || REPLACE(REPLACE(l_input_text, '"', '\"'
), CHR(10), '\n') || '",
                        "apiFormat": "COHERE",
                        "maxTokens": 2048
                      }
                    }';

                    apex_debug.message('📤 Summary Payload: %s', SUBSTR(l_paylo
ad, 1, 4000));

                    l_response_struct := DBMS_CLOUD.SEND_REQUEST(
                        credential_name => 'OCI$RESOURCE_PRINCIPAL',
                        uri             => l_reasoning_endpoint,
                        method          => 'POST',
                        headers         => JSON_OBJECT('Content-Type' VALUE 'app
lication/json'),
                        body            => UTL_RAW.CAST_TO_RAW(l_payload)
                    );

                    l_reasoning_response := DBMS_CLOUD.GET_RESPONSE_TEXT(l_resp
onse_struct);
                    apex_debug.message('📥 Raw Summary Response: %s', SUBSTR(l_r
easoning_response, 1, 4000));

                    l_resp_obj := JSON_OBJECT_T.parse(l_reasoning_response);

                    IF l_resp_obj.has('chatResponse') THEN
                        v_summary_text := l_resp_obj.get_Object('chatResponse').
get_String('text');

                        apex_debug.message('✅ Parsed Summary: %s', SUBSTR(v_sum
mary_text, 1, 4000));

                        UPDATE ai_chat_log
                          SET summary_text = v_summary_text,
                              reasoned_message = v_reasoned_message
                        WHERE id = v_log_row_id;

                        apex_debug.message('🧾 Summary stored in ai_chat_log');

                    ELSE
                        apex_debug.message('⚠️ chatResponse not found in respons
e');
                    END IF;

                EXCEPTION
                    WHEN OTHERS THEN
                        apex_debug.message('❌ Summary generation failed: %s', SQ
LERRM);
                END;
                EXIT;
            ELSE
                apex_debug.message('⚠️ SQL produced no results.');
                v_last_failed := 'Y';
            END IF;

        EXCEPTION
            WHEN OTHERS THEN
                apex_debug.message('❌ Exception in SQL step: %s', SQLERRM);
                IF DBMS_SQL.IS_OPEN(l_cursor) THEN
                    DBMS_SQL.CLOSE_CURSOR(l_cursor);
                END IF;
                v_last_failed := 'Y';
        END;

        -- Step 2: Run Reasoning
        IF v_last_failed = 'Y' AND v_attempt < v_max_attempts THEN
            apex_debug.message('🧠 Triggering reasoning agent');

            l_input_text := NVL(v_reasoned_message, p_user_message);

            l_prompt := 'Rephrase the following business question by replacing
informal IT terms (e.g., "RAM") with their corresponding enterprise equivalents
(e.g., "memory") that arey used in the database. Preserve the original structure
, intent, and meaning of the question. Only substitute terms where necessary and
 ensure the rephrased question remains as close as possible to the original. Res
pond only with the rephrased question. No explanation.';

            -- Combine prompt + user input in the message
            l_input_text := l_prompt || CHR(10) || CHR(10) || l_input_text;

            l_payload := '{
            "compartmentId": "' || p_compartment_id || '",
            "servingMode": {
                "modelId": "cohere.command-a-03-2025",
                "servingType": "ON_DEMAND"
            },
            "chatRequest": {
                "message": "' || REPLACE(REPLACE(l_input_text, '"', '\"'), CHR(1
0), '\n') || '",
                "apiFormat": "COHERE",
                "maxTokens": 2048
            }
            }';

            apex_debug.message('📤 Sending reasoning request');

            l_response_struct := DBMS_CLOUD.SEND_REQUEST(
                credential_name => 'OCI$RESOURCE_PRINCIPAL',
                uri             => l_reasoning_endpoint,
                method          => 'POST',
                headers         => JSON_OBJECT('Content-Type' VALUE 'application
/json'),
                body            => UTL_RAW.CAST_TO_RAW(l_payload)
            );

            l_reasoning_response := DBMS_CLOUD.GET_RESPONSE_TEXT(l_response_str
uct);
            apex_debug.message('📥 Reasoning raw response: %s', SUBSTR(l_reasoni
ng_response, 1, 4000));

            l_resp_obj := JSON_OBJECT_T.parse(l_reasoning_response);

            IF l_resp_obj.has('chatResponse') THEN
                l_result_text := l_resp_obj.get_Object('chatResponse').get_Strin
g('text');
                v_reasoned_message := l_result_text;

                apex_debug.message('✅ Reasoned message: %s', l_result_text);

                INSERT INTO ai_chat_log_reasoning (
                    chat_id, log_id, input_message, rephrased_output,
                    attempt_number, app_user, created_at
                ) VALUES (
                    p_chat_id, NULL, l_input_text, l_result_text,
                    v_attempt, p_app_user, SYSTIMESTAMP
                ) RETURNING id INTO v_reasoning_row_id;
            ELSE
                apex_debug.message('❌ Reasoning "chatResponse" not found in resp
onse');
                v_last_failed := 'Y';
            END IF;
        ELSE
            EXIT WHEN v_attempt >= v_max_attempts;
        END IF;

    END LOOP;

    IF v_last_failed = 'Y' THEN
        apex_debug.message('❌ Final failure after %s attempts', v_attempt);
        RAISE_APPLICATION_ERROR(-20010, '❌ All AI attempts failed to generate a
working SQL query.');
    END IF;

    apex_debug.message('🎉 Procedure completed successfully');
END;
/


  CREATE OR REPLACE EDITIONABLE PROCEDURE "OCI_FOCUS_REPORTS"."PAGE1_CONS_WRKLD_
WEEK_CHART_DATA_PROC" AS
  l_title   VARCHAR2(400);
  l_value   CLOB;
BEGIN
  -- Truncate the entire table before inserting fresh data
  EXECUTE IMMEDIATE 'TRUNCATE TABLE PAGE1_CONS_WRKLD_WEEK_CHART_DATA';

  -- Loop through top N rows by row_number
  FOR rec IN (
    SELECT DBMS_LOB.SUBSTR(WORKLOAD_NAME, 4000) AS WORKLOAD_NAME,
           DBMS_LOB.SUBSTR(VALUE, 4000) AS COMPARTMENTS,
           ROW_NUMBER() OVER (ORDER BY WORKLOAD_NAME) AS rn
    FROM OCI_WORKLOADS
    WHERE VALUE IS NOT NULL
  ) LOOP
    -- Skip if compartment list is empty
    IF rec.COMPARTMENTS IS NOT NULL THEN
      -- Insert new aggregated data
      INSERT INTO PAGE1_CONS_WRKLD_WEEK_CHART_DATA (
        WORKLOAD_NAME,
        WEEK_START,
        COST,
        LAST_REFRESH
      )
      SELECT
        rec.WORKLOAD_NAME,
        TRUNC(CHARGEPERIODEND, 'IW') AS WEEK_START,
        SUM(BILLEDCOST) AS COST,
        SYSDATE
      FROM FOCUS_REPORTS_PY
      WHERE CHARGEPERIODEND >= TRUNC(SYSDATE, 'IW') - INTERVAL '56' DAY
        AND CHARGEPERIODEND < TRUNC(SYSDATE, 'IW') -- Exclude current week
        AND OCI_COMPARTMENTID IN (
          SELECT TRIM(column_value)
          FROM TABLE(APEX_STRING.SPLIT(rec.COMPARTMENTS, ','))
        )
      GROUP BY TRUNC(CHARGEPERIODEND, 'IW');
    END IF;
  END LOOP;
  -- Ensure all changes are committed
  COMMIT;
END;
/


  CREATE OR REPLACE EDITIONABLE PROCEDURE "OCI_FOCUS_REPORTS"."REFRESH_COST_USAG
E_TS_PROC" AS
BEGIN
  EXECUTE IMMEDIATE 'TRUNCATE TABLE COST_USAGE_TIMESERIES';

  FOR granularity IN (
    SELECT 'DAY' AS g FROM DUAL UNION ALL
    SELECT 'WEEK' FROM DUAL UNION ALL
    SELECT 'MONTH' FROM DUAL
  ) LOOP
    INSERT INTO COST_USAGE_TIMESERIES (
      DATE_BUCKET, GRANULARITY,
      BILLINGACCOUNTID, SUBACCOUNTNAME, INVOICEISSUER, REGION, BILLINGCURRENCY,
      SERVICECATEGORY, SERVICENAME, CHARGEDESCRIPTION, RESOURCETYPE, RESOURCEID,

      SKUID, PRICINGUNIT, OCI_COMPARTMENTID, OCI_COMPARTMENTNAME, USAGEUNIT,
      COST, USAGE, LAST_REFRESH
    )
    SELECT
      CASE granularity.g
        WHEN 'DAY' THEN TRUNC(CHARGEPERIODSTART, 'DDD')
        WHEN 'WEEK' THEN TRUNC(CHARGEPERIODSTART, 'IW')
        WHEN 'MONTH' THEN TRUNC(CHARGEPERIODSTART, 'MM')
      END AS DATE_BUCKET,
      granularity.g,
      BILLINGACCOUNTID, SUBACCOUNTNAME, INVOICEISSUER, REGION, BILLINGCURRENCY,
      NVL(SERVICECATEGORY, 'None'), SERVICENAME, CHARGEDESCRIPTION, RESOURCETYPE
, RESOURCEID,
      SKUID, PRICINGUNIT, OCI_COMPARTMENTID, OCI_COMPARTMENTNAME, USAGEUNIT,
      SUM(BILLEDCOST),
      SUM(
        CASE
          WHEN LOWER(USAGEUNIT) LIKE '%month%' THEN USAGEQUANTITY * (730/24)
          ELSE USAGEQUANTITY / 24
        END
      ),
      SYSDATE
    FROM FOCUS_REPORTS_PY
    WHERE CHARGEPERIODEND <= ADD_MONTHS(CHARGEPERIODSTART, 7)
    GROUP BY
      CASE granularity.g
        WHEN 'DAY' THEN TRUNC(CHARGEPERIODSTART, 'DDD')
        WHEN 'WEEK' THEN TRUNC(CHARGEPERIODSTART, 'IW')
        WHEN 'MONTH' THEN TRUNC(CHARGEPERIODSTART, 'MM')
      END,
      BILLINGACCOUNTID, SUBACCOUNTNAME, INVOICEISSUER, REGION, BILLINGCURRENCY,
      SERVICECATEGORY, SERVICENAME, CHARGEDESCRIPTION, RESOURCETYPE, RESOURCEID,

      SKUID, PRICINGUNIT, OCI_COMPARTMENTID, OCI_COMPARTMENTNAME, USAGEUNIT;
  END LOOP;

  -- Finalize the transaction
  COMMIT;
END;
/


  CREATE OR REPLACE EDITIONABLE PROCEDURE "OCI_FOCUS_REPORTS"."PAGE1_CONS_WRKLD_
MONTH_CHART_DATA_PROC" AS
  l_title   VARCHAR2(400);
  l_value   CLOB;
BEGIN
  -- Truncate the table once before processing
  EXECUTE IMMEDIATE 'TRUNCATE TABLE PAGE1_CONS_WRKLD_MONTH_CHART_DATA';

  -- Loop through top N rows by row_number
  FOR rec IN (
    SELECT DBMS_LOB.SUBSTR(WORKLOAD_NAME, 4000) AS WORKLOAD_NAME,
           DBMS_LOB.SUBSTR(VALUE, 4000) AS COMPARTMENTS,
           ROW_NUMBER() OVER (ORDER BY WORKLOAD_NAME) AS rn
    FROM OCI_WORKLOADS
    WHERE VALUE IS NOT NULL
  ) LOOP
    -- Skip empty compartment lists
    IF rec.COMPARTMENTS IS NOT NULL THEN
      -- Insert aggregated data
      INSERT INTO PAGE1_CONS_WRKLD_MONTH_CHART_DATA (
        WORKLOAD_NAME,
        MONTH,
        COST,
        LAST_REFRESH
      )
      SELECT
        rec.WORKLOAD_NAME,
        TRUNC(CHARGEPERIODEND, 'MM') AS MONTH,
        SUM(BILLEDCOST) AS COST,
        SYSDATE
      FROM FOCUS_REPORTS_PY
      WHERE CHARGEPERIODEND >= ADD_MONTHS(TRUNC(SYSDATE, 'MM'), -12)
        AND OCI_COMPARTMENTID IN (
          SELECT TRIM(column_value)
          FROM TABLE(APEX_STRING.SPLIT(rec.COMPARTMENTS, ','))
        )
      GROUP BY TRUNC(CHARGEPERIODEND, 'MM');
    END IF;
  END LOOP;
  -- Ensure all changes are committed
  COMMIT;
END;
/


  CREATE MATERIALIZED VIEW "OCI_FOCUS_REPORTS"."FILTER_VALUES_MV" ("SUBACCOUNTNA
ME", "BILLINGACCOUNTID", "REGION", "OCI_COMPARTMENTID", "SERVICECATEGORY", "SERV
ICENAME", "CHARGEDESCRIPTION", "RESOURCETYPE", "RESOURCEID", "RESOURCENAME")
  SEGMENT CREATION IMMEDIATE
  ORGANIZATION HEAP PCTFREE 10 PCTUSED 40 INITRANS 10 MAXTRANS 255
 COLUMN STORE COMPRESS FOR QUERY HIGH ROW LEVEL LOCKING LOGGING
  BUILD IMMEDIATE
  USING INDEX
  REFRESH COMPLETE ON DEMAND
  USING DEFAULT LOCAL ROLLBACK SEGMENT
  USING ENFORCED CONSTRAINTS DISABLE ON QUERY COMPUTATION DISABLE QUERY REWRITE
DISABLE CONCURRENT REFRESH
  AS SELECT DISTINCT
  fr.SUBACCOUNTNAME,
  fr.BILLINGACCOUNTID,
  fr.REGION,
  fr.OCI_COMPARTMENTID,
  fr.SERVICECATEGORY,
  fr.SERVICENAME,
  fr.CHARGEDESCRIPTION,
  fr.RESOURCETYPE,
  fr.RESOURCEID,
  r.DISPLAY_NAME AS RESOURCENAME
FROM FOCUS_REPORTS_PY fr
LEFT JOIN OCI_RESOURCES_PY r
  ON r.IDENTIFIER = fr.RESOURCEID
  WHERE fr.REGION != 'Commitment Expiration';


  CREATE MATERIALIZED VIEW "OCI_FOCUS_REPORTS"."RATECARD_MV" ("CHARGEDESCRIPTION
", "PRICINGUNIT", "SKUID", "ACTUALUNITPRICE", "LISTUNITPRICE")
  SEGMENT CREATION IMMEDIATE
  ORGANIZATION HEAP PCTFREE 10 PCTUSED 40 INITRANS 10 MAXTRANS 255
 COLUMN STORE COMPRESS FOR QUERY HIGH ROW LEVEL LOCKING LOGGING
  BUILD IMMEDIATE
  USING INDEX
  REFRESH COMPLETE ON DEMAND START WITH sysdate+0 NEXT TO_DATE(SYSDATE + 1)
  USING DEFAULT LOCAL ROLLBACK SEGMENT
  USING ENFORCED CONSTRAINTS DISABLE ON QUERY COMPUTATION DISABLE QUERY REWRITE
DISABLE CONCURRENT REFRESH
  AS SELECT
    CHARGEDESCRIPTION,
    PRICINGUNIT,
    MIN(SKUID) AS SKUID,
    AVG(ROUND(EFFECTIVECOST/PRICINGQUANTITY, 4)) AS ACTUALUNITPRICE,
    MAX(LISTUNITPRICE) AS LISTUNITPRICE
FROM
    FOCUS_REPORTS_PY
WHERE
    PRICINGQUANTITY > 0
AND CHARGEDESCRIPTION NOT LIKE UPPER('%FREE%')
AND BILLINGACCOUNTID='9379274'
AND CHARGECATEGORY='Usage'
GROUP BY
    BILLINGACCOUNTID,
    CHARGEDESCRIPTION,
    PRICINGUNIT;

