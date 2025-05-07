CREATE TABLE USAGE.OCI_SUBSCRIPTIONS_PY 
    ( 
     SUBSCRIPTION_ID            VARCHAR2 (100) , 
     ISO_CODE                   VARCHAR2 (10) , 
     NAME                       VARCHAR2 (100) , 
     STD_PRECISION              NUMBER , 
     SERVICE_NAME               VARCHAR2 (100) , 
     STATUS                     VARCHAR2 (50) , 
     AVAILABLE_AMOUNT           VARCHAR2 (100) , 
     BOOKING_OPTY_NUMBER        VARCHAR2 (100) , 
     COMMITMENT_SERVICES        CLOB , 
     CSI                        VARCHAR2 (100) , 
     DATA_CENTER_REGION         VARCHAR2 (100) , 
     FUNDED_ALLOCATION_VALUE    VARCHAR2 (100) , 
     ID                         VARCHAR2 (100) , 
     IS_INTENT_TO_PAY           VARCHAR2 (10) , 
     NET_UNIT_PRICE             VARCHAR2 (100) , 
     OPERATION_TYPE             VARCHAR2 (100) , 
     ORDER_NUMBER               VARCHAR2 (100) , 
     ORIGINAL_PROMO_AMOUNT      VARCHAR2 (100) , 
     PARTNER_TRANSACTION_TYPE   VARCHAR2 (100) , 
     PRICING_MODEL              VARCHAR2 (100) , 
     PRODUCT_NAME               VARCHAR2 (200) , 
     PRODUCT_PART_NUMBER        VARCHAR2 (100) , 
     PRODUCT_PROVISIONING_GROUP VARCHAR2 (100) , 
     PRODUCT_UNIT_OF_MEASURE    VARCHAR2 (100) , 
     PROGRAM_TYPE               VARCHAR2 (100) , 
     PROMO_TYPE                 VARCHAR2 (100) , 
     QUANTITY                   VARCHAR2 (100) , 
     SUBSTATUS                  VARCHAR2 (100) , 
     TIME_END                   VARCHAR2 (50) , 
     TIME_START                 VARCHAR2 (50) , 
     TOTAL_VALUE                VARCHAR2 (100) , 
     USED_AMOUNT                VARCHAR2 (100) 
    ) 
    TABLESPACE DATA 
    LOGGING 
;