#!/bin/bash

set -euo pipefail

CONFIG_FILE="/home/opc/config.configured.json"
COMPARTMENT_ID=$(awk -F': ' '/^compartment_id:/ {print $2}' "$CONFIG_FILE")
AI_AGENT_ID=$(cat /home/opc/gen_ai_agent_id.txt)
AI_AGENT_ENDPOINT_ID=$(cat /home/opc/gen_ai_agent_endpoint_id.txt)
AI_AGENT_TOOL_ID=$(cat /home/opc/sql_tool_ocid.txt)

# --- Step 1: Delete SQL Tool ---
echo "Deleting AI SQL Tool: $AI_AGENT_TOOL_ID"
oci generative-ai-agent tool delete \
  --tool-id "$AI_AGENT_TOOL_ID" \
  --force \
  --wait-for-state SUCCEEDED \
  --wait-for-state FAILED

if [ $? -eq 0 ]; then
  echo "✅ SQL Tool deleted successfully."
  read -p "Press Enter to remove SQL tool file..."
  rm -f /home/opc/sql_tool_ocid.txt
else
  echo "❌ Failed to delete SQL Tool."
  exit 1
fi

# --- Step 2: Delete Endpoint ---
echo "Deleting AI Agent Endpoint: $AI_AGENT_ENDPOINT_ID"
oci generative-ai-agent agent-endpoint delete \
  --agent-endpoint-id "$AI_AGENT_ENDPOINT_ID" \
  --force \
  --wait-for-state SUCCEEDED \
  --wait-for-state FAILED

if [ $? -eq 0 ]; then
  echo "✅ Agent Endpoint deleted successfully."
  read -p "Press Enter to remove agent endpoint file..."
  rm -f /home/opc/gen_ai_agent_endpoint_id.txt
else
  echo "❌ Failed to delete Agent Endpoint."
  exit 1
fi

# --- Step 3: Delete Agent ---
echo "Deleting AI Agent: $AI_AGENT_ID"
oci generative-ai-agent agent delete \
  --agent-id "$AI_AGENT_ID" \
  --force \
  --wait-for-state SUCCEEDED \
  --wait-for-state FAILED

if [ $? -eq 0 ]; then
  echo "✅ Agent deleted successfully."
  read -p "Press Enter to remove agent file..."
  rm -f /home/opc/gen_ai_agent_id.txt
else
  echo "❌ Failed to delete Agent."
  exit 1
fi