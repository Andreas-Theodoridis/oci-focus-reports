#!/bin/bash

# Set PATH (optional)
export PATH=$PATH:/usr/local/bin

OCID_FILE="./.adb_ocid"
COMPUTE_FILE="./.compute_count_up"

if [ ! -f "$OCID_FILE" ] || [ ! -f "$COMPUTE_FILE" ]; then
  echo "Enter the Autonomous Database OCID:"
  read ADB_OCID

  echo "Enter the desired ECPU count for scaling UP:"
  read COMPUTE_COUNT

  echo "$ADB_OCID" > "$OCID_FILE"
  echo "$COMPUTE_COUNT" > "$COMPUTE_FILE"
else
  ADB_OCID=$(cat "$OCID_FILE")
  COMPUTE_COUNT=$(cat "$COMPUTE_FILE")
fi

echo "Scaling UP ADB OCID: $ADB_OCID to Compute Count: $COMPUTE_COUNT"
LOG_PATH="/home/opc/oci-focus-reports/logs/update_db_up.log"

oci db autonomous-database update \
  --autonomous-database-id "$ADB_OCID" \
  --compute-count "$COMPUTE_COUNT" \
  >> "$LOG_PATH" 2>&1
