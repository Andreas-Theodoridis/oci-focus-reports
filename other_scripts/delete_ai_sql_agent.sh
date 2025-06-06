#!/bin/bash

# Extract compartment_id from the file
CONFIG_FILE="/home/opc/config.configured.json"
COMPARTMENT_ID=$(awk -F': ' '/^compartment_id:/ {print $2}' "$CONFIG_FILE")
AI_AGENT_ID=$(cat /home/opc/gen_ai_agent_id.txt)
AI_AGENT_ENDPOINT_ID=$(cat /home/opc/gen_ai_agent_endpoint_id.txt)
AI_AGENT_TOOL_ID=$(cat /home/opc/sql_tool_ocid.txt)

# Delete tool
oci generative-ai-agent tool delete --tool-id $AI_AGENT_TOOL_ID --force --wait-for-state SUCCEEDED --wait-for-state FAILED
rm -Rf /home/opc/sql_tool_ocid.txt;

# Delete Endpoint
oci generative-ai-agent agent-endpoint delete --agent-endpoint-id $AI_AGENT_ENDPOINT_ID --force --wait-for-state SUCCEEDED --wait-for-state FAILED
rm -Rf /home/opc/gen_ai_agent_endpoint_id.txt;

# Delete Agent 
oci generative-ai-agent agent delete --agent-id $AI_AGENT_ID --force --wait-for-state SUCCEEDED --wait-for-state FAILED
rm -Rf /home/opc/gen_ai_agent_id.txt