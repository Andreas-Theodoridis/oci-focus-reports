#!/bin/bash

# Extract compartment_id from the file
CONFIG_FILE="/home/opc/config.configured.json"
COMPARTMENT_ID=$(awk -F': ' '/^compartment_id:/ {print $2}' "$CONFIG_FILE")
DB_TOOLS_ID=$(awk -F': ' '/^db_tools_id:/ {print $2}' "$CONFIG_FILE")
OBJECT_STRG_NS=$(awk -F': ' '/^object_strg_ns:/ {print $2}' "$CONFIG_FILE")
BUCKET_NAME=$(awk -F': ' '/^bucket_name:/ {print $2}' "$CONFIG_FILE")
AI_TOOL_SQL_SCHEMA=$(awk -F': ' '/^ai_agent_tool_sql_schema:/ {print $2}' "$CONFIG_FILE")
AI_TOOL_ICL_EXAMPLES=$(awk -F': ' '/^ai_agent_tool_icl_examples:/ {print $2}' "$CONFIG_FILE")
AI_TOOL_TABLE_DESCRIPTIONS=$(awk -F': ' '/^ai_agent_tool_table_descriptionss:/ {print $2}' "$CONFIG_FILE")

# Step 1: Create the AI Agent and capture its OCID
echo "Creating OCI AI Agent..."
AI_AGENT_JSON=$(oci generative-ai-agent agent create \
  --compartment-id "$COMPARTMENT_ID" \
  --display-name "Focus-Reports-SQL-Agent" \
  --description "Focus Reports SQL Agent for OVBot" \
  --query 'data.id' --raw-output)

# Optional: Check if the agent was created
if [[ -z "$AI_AGENT_JSON" ]]; then
  echo "Failed to create AI Agent."
  exit 1
fi

echo "AI Agent OCID: $AI_AGENT_JSON"

# Step 2: Create the AI Agent endpoint
oci generative-ai-agent agent-endpoint create \
    --agent-id "$AI_AGENT_JSON" \
    --compartment-id "$COMPARTMENT_ID"

# Step 3: Create OCI AI SQL Tool
echo "Creating OCI AI SQL Tool..."
oci generative-ai-agent tool create-tool-sql-tool-config \
  --agent-id "$AI_AGENT_JSON" \
  --compartment-id "$COMPARTMENT_ID" \
  --display-name "SQLTool" \
  --description "Focus Reports AI SQL Agent Config" \
  --tool-config-database-connection '{
    "connectionId": "$DB_TOOLS_ID",
    "connectionType": "DATABASE_TOOL_CONNECTION"
  }' \
  --tool-config-database-schema '{
    "inputLocationType": "OBJECT_STORAGE_PREFIX",
    "namespaceName": "$OBJECT_STRG_NS",
    "bucketName": "$BUCKET_NAME",
    "prefix": "$AI_TOOL_SQL_SCHEMA"
  }' \
  --tool-config-icl-examples '{
    "inputLocationType": "OBJECT_STORAGE_PREFIX",
    "namespaceName": "$OBJECT_STRG_NS",
    "bucketName": "$BUCKET_NAME",
    "prefix": "$AI_TOOL_ICL_EXAMPLES"
  }' \
  --tool-config-table-and-column-description '{
    "inputLocationType": "OBJECT_STORAGE_PREFIX",
    "namespaceName": "$OBJECT_STRG_NS}",
    "bucketName": "$BUCKET_NAME",
    "prefix": "$AI_TOOL_TABLE_DESCRIPTIONS"
  }' \
  --tool-config-generation-llm-customization file:///home/opc/oci-focus-reports/config/llm_instruction.json \
  --tool-config-should-enable-sql-execution true \
  --tool-config-should-enable-self-correction true \
  --tool-config-dialect ORACLE_SQL \
  --tool-config-model-size LARGE \
  --query 'data.id' --raw-output > /home/opc/sql_tool_ocid.txt"