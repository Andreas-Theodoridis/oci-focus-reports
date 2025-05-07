
create table "OCI_FOCUS_REPORTS"."FOCUS_REPORTS_PY" (
   "AVAILABILITYZONE"           varchar2(100) collate "USING_NLS_COMP",
   "BILLEDCOST"                 number,
   "BILLINGACCOUNTID"           number,
   "BILLINGACCOUNTNAME"         varchar2(100) collate "USING_NLS_COMP",
   "BILLINGCURRENCY"            varchar2(20) collate "USING_NLS_COMP",
   "BILLINGPERIODEND"           timestamp(6),
   "BILLINGPERIODSTART"         timestamp(6),
   "CHARGECATEGORY"             varchar2(200) collate "USING_NLS_COMP",
   "CHARGEDESCRIPTION"          varchar2(512) collate "USING_NLS_COMP",
   "CHARGEFREQUENCY"            varchar2(100) collate "USING_NLS_COMP",
   "CHARGEPERIODEND"            timestamp(6),
   "CHARGEPERIODSTART"          timestamp(6),
   "CHARGESUBCATEGORY"          varchar2(200) collate "USING_NLS_COMP",
   "COMMITMENTDISCOUNTCATEGORY" varchar2(200) collate "USING_NLS_COMP",
   "COMMITMENTDISCOUNTID"       varchar2(200) collate "USING_NLS_COMP",
   "COMMITMENTDISCOUNTNAME"     varchar2(200) collate "USING_NLS_COMP",
   "COMMITMENTDISCOUNTTYPE"     varchar2(200) collate "USING_NLS_COMP",
   "EFFECTIVECOST"              number,
   "INVOICEISSUER"              varchar2(100) collate "USING_NLS_COMP",
   "LISTCOST"                   number,
   "LISTUNITPRICE"              number,
   "PRICINGCATEGORY"            varchar2(100) collate "USING_NLS_COMP",
   "PRICINGQUANTITY"            number,
   "PRICINGUNIT"                varchar2(200) collate "USING_NLS_COMP",
   "PROVIDER"                   varchar2(200) collate "USING_NLS_COMP",
   "PUBLISHER"                  varchar2(200) collate "USING_NLS_COMP",
   "REGION"                     varchar2(200) collate "USING_NLS_COMP",
   "RESOURCEID"                 varchar2(200) collate "USING_NLS_COMP",
   "RESOURCENAME"               varchar2(1000) collate "USING_NLS_COMP",
   "RESOURCETYPE"               varchar2(200) collate "USING_NLS_COMP",
   "SERVICECATEGORY"            varchar2(200) collate "USING_NLS_COMP",
   "SERVICENAME"                varchar2(1000) collate "USING_NLS_COMP",
   "SKUID"                      varchar2(20) collate "USING_NLS_COMP",
   "SKUPRICEID"                 varchar2(100) collate "USING_NLS_COMP",
   "SUBACCOUNTID"               varchar2(100) collate "USING_NLS_COMP",
   "SUBACCOUNTNAME"             varchar2(100) collate "USING_NLS_COMP",
   "TAGS"                       clob collate "USING_NLS_COMP",
   "USAGEQUANTITY"              number,
   "USAGEUNIT"                  varchar2(1000) collate "USING_NLS_COMP",
   "OCI_REFERENCENUMBER"        varchar2(1000) collate "USING_NLS_COMP",
   "OCI_COMPARTMENTID"          varchar2(1000) collate "USING_NLS_COMP",
   "OCI_COMPARTMENTNAME"        varchar2(1000) collate "USING_NLS_COMP",
   "OCI_OVERAGEFLAG"            varchar2(100) collate "USING_NLS_COMP",
   "OCI_UNITPRICEOVERAGE"       varchar2(100) collate "USING_NLS_COMP",
   "OCI_BILLEDQUANTITYOVERAGE"  varchar2(100) collate "USING_NLS_COMP",
   "OCI_COSTOVERAGE"            varchar2(100) collate "USING_NLS_COMP",
   "OCI_ATTRIBUTEDUSAGE"        number,
   "OCI_ATTRIBUTEDCOST"         number,
   "OCI_BACKREFERENCENUMBER"    varchar2(1000) collate "USING_NLS_COMP"
) 
    TABLESPACE DATA 
    LOGGING 
    PARTITION BY RANGE ("CHARGEPERIODSTART")
        INTERVAL (NUMTOYMINTERVAL(1, 'MONTH'))
        (
        PARTITION p_initial VALUES LESS THAN (TO_DATE('2022-01-01', 'YYYY-MM-DD'))
)
;
