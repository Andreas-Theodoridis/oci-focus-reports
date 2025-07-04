#!/bin/bash

# Prompt to run git_update.sh
read -p "Do you want to run update files from gi? (yes/no): " answer1
if [[ "$answer1" =~ ^[Yy][Ee][Ss]$ || "$answer1" =~ ^[Yy]$ ]]; then
  /home/opc/oci-focus-reports/other_scripts/git_update.sh
else
  echo "Skipped git_update.sh"
fi

# Prompt to run db_apex_upgrade.py
read -p "Do you want to update database and application? (yes/no): " answer2
if [[ "$answer2" =~ ^[Yy][Ee][Ss]$ || "$answer2" =~ ^[Yy]$ ]]; then
  /home/opc/oci-focus-reports/python_scripts/db_apex_upgrade.py
else
  echo "Skipped db_apex_upgrade.py"
fi