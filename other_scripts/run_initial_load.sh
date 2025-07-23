#!/bin/bash

SCRIPT_DIR="/home/opc/oci-focus-reports/python_scripts"

declare -a scripts=(
    "availability_metrics_initial_load.py"
    "oci_compartments.py"
    "oci_resources.py"
    "subscriptions.py"
    "focus_reports_initial_load.py"
)

# Prompt for EXA
echo "❓ Do you want to run oci_exa_maintenance_details.py? (y/n): "
read -r run_exa

echo "🔁 Starting execution of reporting scripts..."

for script in "${scripts[@]}"; do
    echo "🚀 Running $script..."
    python3 "$SCRIPT_DIR/$script"
    echo "✅ Finished $script"
    echo ""
done

if [[ "$run_exa" =~ ^[Yy]$ ]]; then
    echo "🚀 Running oci_exa_maintenance_details.py..."
    python3 "$SCRIPT_DIR/oci_exa_maintenance_details.py"
    echo "✅ Finished oci_exa_maintenance_details.py"
else
    echo "⏭️ Skipped oci_exa_maintenance_details.py"
fi

echo "🎉 All done!"