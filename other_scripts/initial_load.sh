#!/bin/bash
nohup bash /home/opc/oci-focus-reports/other_scripts/run_initial_load.sh > /home/opc/oci-focus-reports/logs/initial_load_log_$(date +%Y%m%d_%H%M%S).log 2>&1