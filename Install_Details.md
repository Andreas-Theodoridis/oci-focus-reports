Login to newly created compute and check cloud init script progress and successful completion:
tail -f /var/log/cloud-init-output.log

Once completed successfully, relogin to vm!


Go to directory:
cd /home/opc/oci-focus-reports/db_scripts
And install create_apex_workspace.sql => sqlplus admin@fcradw_high @create_apex_workspace.sql
When APEX workspace is installed, install app => sqlplus oci_focus_reports@fcradw_high @install_observantage_app.sql
Once application is installed, login to APEX workspace:
WORKSPACE: OCI_FOCUS_REPORTS
USERNAME: OCI_FOCUS_REPORTS
PASSWORD: <<your_password_used_in_terraform_variables>>

Then, select the newly created app (Application 100) => Supporting Objects => Far right menu (Tasks) => Install Supporting Objects

ObserVantage uses OCI's Domain Identity Authentication so you need to alter the credentials inside the APEX App:
Find OAuth credentials: Login to OCI Console -> Identity & Security -> Domains -> Default domain (under root compartment) 
Copy from detail -> Domain URL
In Integrated applications -> Focus Reports APEX OAuth App -> OAuth Configuration and copy Client ID and secret

Login to OCI_FOCUS_REPORTS Workspace -> Focus Cost Reporting application -> Share Components -> Authentication Schemes -> OCI IAM OAuth and edit: 
Dicsovery URL -> Domain URL/.well-known/openid-configuration
Go to  OCI_FOCUS_REPORTS Workspace -> App Builder -> Workspace Utilities -> Web Credentials -> OCI OAuth Credentials -> Edit:
Client ID or Username -> Client ID
Client Secret or Password -> secret



Run below script for initial load:
/home/opc/oci-focus-reports/other_scripts/initial_load.sh

Creae SQL AI Agent (it may take a few minutes to complete, please check OCI Console):
/home/opc/oci-focus-reports/other_scripts/create_ai_sql_agent.sh

/*Initial Load:
Login to VM:
Edit config.json:
"use_dynamic_prefix": true -> "use_dynamic_prefix": false

After Initial Load:
"use_dynamic_prefix": false -> "use_dynamic_prefix": true
Run all python scripts in /home/opc/oci-focus-reports/python_scripts except compress_old_focus_report_csv.py and oci_exa_maintenance_details.py unless you are an ExaCC/ExaDedicated customer*/

For OVChat:

Create Credentials for focus-reports-user => Create API Key
Go to Workspace Home => Workspace Credentials => Web Credentials => modify ca_user_for_oci and enter details from the API key created above
Got to App => Page 6 => Pre-Rendering => Before Regions => Computations => P6_SQL_AGENT_ID => Static ID => Enter OCID of the newly created Agent Endpoint: ocid1.genaiagentendpoint.oc1.eu-frankfurt-1.amaaaaaaxnbdvtaa5wk2njppjcqa5lpgcqdsumfwaaozb77lkkjn6pd4e3aa 