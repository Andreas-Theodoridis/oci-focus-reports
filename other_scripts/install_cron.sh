#!/bin/bash

# Temp file to hold current crontab
TEMP_CRON=$(mktemp)

# Get current crontab (if any)
crontab -l > "$TEMP_CRON" 2>/dev/null

# Define the new entries
CRON_ENTRIES=$(cat <<'EOF'
0 */6 * * * /usr/bin/python /home/opc/oci_extensions/python_scripts/focus_reports_daily_load_with_logs.py >> /home/opc/oci_extensions/logs/fc_6H_crontab.log 2>&1
0 */6 * * * /usr/bin/python /home/opc/oci_extensions/python_scripts/availability_metrics.py >> /home/opc/oci_extensions/logs/availability_6H_crontab.log 2>&1
0 1 * * * /usr/bin/python /home/opc/oci_extensions/python_scripts/subscriptions.py >> /home/opc/oci_extensions/logs/subscriptions_daily_crontab.log 2>&1
0 2 * * * /usr/bin/python /home/opc/oci_extensions/python_scripts/oci_compartments.py >> /home/opc/oci_extensions/logs/gsis_comps_daily_crontab.log 2>&1
0 3 * * * /usr/bin/python /home/opc/oci_extensions/python_scripts/compress_old_focus_report_csv.py >> /home/opc/oci_extensions/logs/compress_old_focus_report_csv.log 2>&1
0 4 * * * /usr/bin/python /home/opc/oci_extensions/python_scripts/oci_resources.py >> /home/opc/oci_extensions/logs/gsis_resources.log 2>&1
30 4 * * * /usr/bin/python /home/opc/oci_extensions/python_scripts/oci_exa_maintenance_details.py >> /home/opc/oci_extensions/logs/oci_exa_maintenance_details.log 2>&1
EOF
)

# Append entries if not already present
while IFS= read -r line; do
    grep -F -- "$line" "$TEMP_CRON" >/dev/null || echo "$line" >> "$TEMP_CRON"
done <<< "$CRON_ENTRIES"

# Install the new crontab
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

echo "✅ Crontab entries updated."
