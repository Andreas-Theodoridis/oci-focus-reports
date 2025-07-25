#!/bin/bash

# Temp file to hold current crontab
TEMP_CRON=$(mktemp)

# Get current crontab (if any)
crontab -l > "$TEMP_CRON" 2>/dev/null

# Define the base entries
CRON_ENTRIES=$(cat <<'EOF'
0 */6 * * * /usr/bin/python /home/opc/oci-focus-reports/python_scripts/focus_reports_daily_load_with_logs.py >> /home/opc/oci-focus-reports/logs/fc_6H_crontab.log 2>&1
0 */6 * * * /usr/bin/python /home/opc/oci-focus-reports/python_scripts/availability_metrics.py >> /home/opc/oci-focus-reports/logs/availability_6H_crontab.log 2>&1
0 1 * * * /usr/bin/python /home/opc/oci-focus-reports/python_scripts/subscriptions.py >> /home/opc/oci-focus-reports/logs/subscriptions_daily_crontab.log 2>&1
0 2 * * * /usr/bin/python /home/opc/oci-focus-reports/python_scripts/oci_compartments.py >> /home/opc/oci-focus-reports/logs/gsis_comps_daily_crontab.log 2>&1
0 3 * * * /usr/bin/python /home/opc/oci-focus-reports/python_scripts/compress_old_focus_report_csv.py >> /home/opc/oci-focus-reports/logs/compress_old_focus_report_csv.log 2>&1
0 4 * * * /usr/bin/python /home/opc/oci-focus-reports/python_scripts/oci_resources.py >> /home/opc/oci-focus-reports/logs/gsis_resources.log 2>&1
0 4 * * * /usr/bin/python /home/opc/oci-focus-reports/python_scripts/oci_aimodels.py >> /home/opc/oci-focus-reports/logs/oci_ai_models.log 2>&1
#30 4 * * * /usr/bin/python /home/opc/oci-focus-reports/python_scripts/oci_exa_maintenance_details.py >> /home/opc/oci-focus-reports/logs/oci_exa_maintenance_details.log 2>&1
EOF
)

# Append base entries if not already present
while IFS= read -r line; do
    grep -F -- "$line" "$TEMP_CRON" >/dev/null || echo "$line" >> "$TEMP_CRON"
done <<< "$CRON_ENTRIES"

# Determine script directory (same directory as this setup script)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Prompt for scale-up job
echo -n "📅 Do you want to also install the ADB scale-up job (scale_up_db.sh) in crontab? [y/N]: "
read -r USER_RESPONSE
if [[ "$USER_RESPONSE" =~ ^[Yy]$ ]]; then
    SCALE_UP_CRON_ENTRY="0 8 * * 1-5 $SCRIPT_DIR/scale_up_db.sh > /home/opc/oci-focus-reports/logs/scale_up.log 2>&1"
    grep -F -- "$SCALE_UP_CRON_ENTRY" "$TEMP_CRON" >/dev/null || echo "$SCALE_UP_CRON_ENTRY" >> "$TEMP_CRON"
    echo "✅ Added scale_up_db.sh to crontab at 08:00 every weekday."
fi

# Prompt for scale-down job
echo -n "📅 Do you want to also install the ADB scale-down job (scale_down_db.sh) in crontab? [y/N]: "
read -r USER_RESPONSE
if [[ "$USER_RESPONSE" =~ ^[Yy]$ ]]; then
    SCALE_DOWN_CRON_ENTRY="0 20 * * * $SCRIPT_DIR/scale_down_db.sh > /home/opc/oci-focus-reports/logs/scale_down.log 2>&1"
    grep -F -- "$SCALE_DOWN_CRON_ENTRY" "$TEMP_CRON" >/dev/null || echo "$SCALE_DOWN_CRON_ENTRY" >> "$TEMP_CRON"
    echo "✅ Added scale_down_db.sh to crontab at 20:00 every day."
fi

# Install the new crontab
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

echo "✅ Crontab entries updated."
