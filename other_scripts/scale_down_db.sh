#!/bin/bash

# Set PATH (optional)
export OCI_CLI_AUTH=instance_principal
export PATH=$PATH:/usr/local/bin

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

OCID_FILE="$SCRIPT_DIR/.adb_ocid"
COMPUTE_FILE="$SCRIPT_DIR/.compute_count_down"
LOG_PATH="$SCRIPT_DIR/update_db_down.log"

if [ ! -f "$OCID_FILE" ] || [ ! -f "$COMPUTE_FILE" ]; then
  echo "Enter the Autonomous Database OCID:"
  read ADB_OCID

  echo "Enter the desired ECPU count for scaling DOWN:"
  read COMPUTE_COUNT

  echo "$ADB_OCID" > "$OCID_FILE"
  echo "$COMPUTE_COUNT" > "$COMPUTE_FILE"
else
  ADB_OCID=$(cat "$OCID_FILE")
  COMPUTE_COUNT=$(cat "$COMPUTE_FILE")
fi

echo "Scaling Down ADB OCID: $ADB_OCID to Compute Count: $COMPUTE_COUNT" >> "$LOG_PATH"

oci db autonomous-database update \
  --autonomous-database-id "$ADB_OCID" \
  --compute-count "$COMPUTE_COUNT"