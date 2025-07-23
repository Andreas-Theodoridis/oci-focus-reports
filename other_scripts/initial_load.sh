#!/bin/bash
echo "❓ Run EXA maintenance script too? (y/n): "
read -r choice

if [[ "$choice" =~ ^[Yy]$ ]]; then
    nohup bash /home/opc/oci-focus-reports/other_scripts/run_initial_load.sh --run-exa > /home/opc/oci-focus-reports/logs/initial_load_log_$(date +%Y%m%d_%H%M%S).log 2>&1 &
else
    nohup bash /home/opc/oci-focus-reports/other_scripts/run_initial_load.sh > /home/opc/oci-focus-reports/logs/initial_load_log_$(date +%Y%m%d_%H%M%S).log 2>&1 &
fi

echo "🟢 Script is running in background. You can safely close the terminal."