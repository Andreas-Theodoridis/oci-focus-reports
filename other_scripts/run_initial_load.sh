#!/bin/bash

SCRIPT_DIR="/home/opc/oci-focus-reports/python_scripts"
LOG_FILE="/home/opc/oci-focus-reports/logs/initial_load_scripts_log_$(date +%Y%m%d_%H%M%S).log"

declare -a scripts=(
    "availability_metrics_initial_load.py"
    "oci_compartments.py"
    "oci_resources.py"
    "subscriptions.py"
    "focus_reports_initial_load.py"
)

# Handle command-line argument for EXA maintenance
RUN_EXA="n"
if [[ "$1" == "--run-exa" ]]; then
    RUN_EXA="y"
fi

{
    echo "🔁 Starting execution of reporting scripts..."

    for script in "${scripts[@]}"; do
        echo "🚀 Running $script..."
        python3 "$SCRIPT_DIR/$script"
        echo "✅ Finished $script"
        echo ""
    done

    rm -Rf /home/opc/oci-focus-reports/data/*

    if [[ "$RUN_EXA" =~ ^[Yy]$ ]]; then
        echo "🚀 Running oci_exa_maintenance_details.py..."
        python3 "$SCRIPT_DIR/oci_exa_maintenance_details.py"
        echo "✅ Finished oci_exa_maintenance_details.py"
    else
        echo "⏭️ Skipped oci_exa_maintenance_details.py"
    fi

    echo "🎉 All done!"
} >> "$LOG_FILE" 2>&1