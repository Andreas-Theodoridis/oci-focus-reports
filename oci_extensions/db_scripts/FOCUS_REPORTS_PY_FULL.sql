create table "USAGE"."FOCUS_REPORTS_PY" (
   "AVAILABILITYZONE"           varchar2(4000) collate "USING_NLS_COMP",
   "BILLEDCOST"                 number,
   "BILLINGACCOUNTID"           number,
   "BILLINGACCOUNTNAME"         varchar2(32767) collate "USING_NLS_COMP",
   "BILLINGCURRENCY"            varchar2(4000) collate "USING_NLS_COMP",
   "BILLINGPERIODEND"           timestamp(6),
   "BILLINGPERIODSTART"         timestamp(6),
   "CHARGECATEGORY"             varchar2(4000) collate "USING_NLS_COMP",
   "CHARGEDESCRIPTION"          varchar2(4000) collate "USING_NLS_COMP",
   "CHARGEFREQUENCY"            varchar2(32767) collate "USING_NLS_COMP",
   "CHARGEPERIODEND"            timestamp(6),
   "CHARGEPERIODSTART"          timestamp(6),
   "CHARGESUBCATEGORY"          varchar2(32767) collate "USING_NLS_COMP",
   "COMMITMENTDISCOUNTCATEGORY" varchar2(32767) collate "USING_NLS_COMP",
   "COMMITMENTDISCOUNTID"       varchar2(32767) collate "USING_NLS_COMP",
   "COMMITMENTDISCOUNTNAME"     varchar2(32767) collate "USING_NLS_COMP",
   "COMMITMENTDISCOUNTTYPE"     varchar2(32767) collate "USING_NLS_COMP",
   "EFFECTIVECOST"              number,
   "INVOICEISSUER"              varchar2(4000) collate "USING_NLS_COMP",
   "LISTCOST"                   number,
   "LISTUNITPRICE"              number,
   "PRICINGCATEGORY"            varchar2(32767) collate "USING_NLS_COMP",
   "PRICINGQUANTITY"            number,
   "PRICINGUNIT"                varchar2(4000) collate "USING_NLS_COMP",
   "PROVIDER"                   varchar2(4000) collate "USING_NLS_COMP",
   "PUBLISHER"                  varchar2(4000) collate "USING_NLS_COMP",
   "REGION"                     varchar2(4000) collate "USING_NLS_COMP",
   "RESOURCEID"                 varchar2(4000) collate "USING_NLS_COMP",
   "RESOURCENAME"               varchar2(32767) collate "USING_NLS_COMP",
   "RESOURCETYPE"               varchar2(4000) collate "USING_NLS_COMP",
   "SERVICECATEGORY"            varchar2(4000) collate "USING_NLS_COMP",
   "SERVICENAME"                varchar2(4000) collate "USING_NLS_COMP",
   "SKUID"                      varchar2(4000) collate "USING_NLS_COMP",
   "SKUPRICEID"                 varchar2(32767) collate "USING_NLS_COMP",
   "SUBACCOUNTID"               varchar2(4000) collate "USING_NLS_COMP",
   "SUBACCOUNTNAME"             varchar2(4000) collate "USING_NLS_COMP",
   "TAGS"                       clob collate "USING_NLS_COMP",
   "USAGEQUANTITY"              number,
   "USAGEUNIT"                  varchar2(4000) collate "USING_NLS_COMP",
   "OCI_REFERENCENUMBER"        varchar2(4000) collate "USING_NLS_COMP",
   "OCI_COMPARTMENTID"          varchar2(4000) collate "USING_NLS_COMP",
   "OCI_COMPARTMENTNAME"        varchar2(4000) collate "USING_NLS_COMP",
   "OCI_OVERAGEFLAG"            varchar2(4000) collate "USING_NLS_COMP",
   "OCI_UNITPRICEOVERAGE"       varchar2(32767) collate "USING_NLS_COMP",
   "OCI_BILLEDQUANTITYOVERAGE"  varchar2(32767) collate "USING_NLS_COMP",
   "OCI_COSTOVERAGE"            varchar2(32767) collate "USING_NLS_COMP",
   "OCI_ATTRIBUTEDUSAGE"        number,
   "OCI_ATTRIBUTEDCOST"         number,
   "OCI_BACKREFERENCENUMBER"    varchar2(4000) collate "USING_NLS_COMP"
) default collation "USING_NLS_COMP"
pctfree 10
pctused 40
initrans 10
maxtrans 255
   storage ( buffer_pool default flash_cache default cell_flash_cache default )
tablespace "DATA"
      lob ( "TAGS" ) store as securefile (
         enable storage in row
         4000
         chunk 8192
         nocache logging
         nocompress
         keep_duplicates
         storage ( buffer_pool default flash_cache default cell_flash_cache default )
      )
      partition by range (
         "CHARGEPERIODSTART"
      ) interval ( numtoyminterval(
         1,
         'MONTH'
      ) ) ( partition "P_BEFORE_2024"
         values less than ( timestamp ' 2024-01-01 00:00:00' )
      segment creation deferred
      pctfree 10 pctused 40 initrans 10 maxtrans 255 nocompress logging
         storage ( buffer_pool default flash_cache default cell_flash_cache default )
      tablespace "DATA"
         lob (
            "TAGS"
         ) store as securefile (
            tablespace "DATA"
            enable storage in row
            4000
            chunk 8192
            nocache logging
            nocompress
            keep_duplicates
            storage ( buffer_pool default flash_cache default cell_flash_cache default )
         )
      )