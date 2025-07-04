Login to newly created compute and check cloud init script progress and successful completion:
tail -f /var/log/cloud-init-output.log

Once completed successfully, relogin to vm!


Go to directory:
cd /home/opc/oci-focus-reports/db_scripts
And install create_apex_workspace.sql => sqlplus admin@fcradw_high @create_apex_workspace.sql
Install OCI_FOCUS_REPORTS db objects: sqlplus oci_focus_reports@fcradw_high @install_ov_db_objects.sql
Install OCI_FOCUS_REPORTS AI db objects: sqlplus oci_focus_reports@fcradw_high @install_ai_config.sq
When APEX workspace is installed, install app => sqlplus oci_focus_reports@fcradw_high @install_observantage_app.sql
Once application is installed, login to APEX workspace:
WORKSPACE: OCI_FOCUS_REPORTS
USERNAME: OCI_FOCUS_REPORTS
PASSWORD: <<your_password_used_in_terraform_variables>>

<!--Then, select the newly created app (Application 100) => Supporting Objects => Far right menu (Tasks) => Install Supporting Objects-->

<!--Optional
ObserVantage uses OCI's Domain Identity Authentication so you need to alter the credentials inside the APEX App:
Find OAuth credentials: Login to OCI Console -> Identity & Security -> Domains -> Default domain (under root compartment) 
Copy from detail -> Domain URL
In Integrated applications -> Focus Reports APEX OAuth App -> OAuth Configuration and copy Client ID and secret

Login to OCI_FOCUS_REPORTS Workspace -> Focus Cost Reporting application -> Share Components -> Authentication Schemes -> OCI IAM OAuth and edit: 
Dicsovery URL -> Domain URL/.well-known/openid-configuration
Go to  OCI_FOCUS_REPORTS Workspace -> App Builder -> Workspace Utilities -> Web Credentials -> OCI OAuth Credentials -> Edit:
Client ID or Username -> Client ID
Client Secret or Password -> secret
-->

Run below script for initial load:
/home/opc/oci-focus-reports/other_scripts/initial_load.sh

Run once scale_up_db.sh and scale_down_db.sh for scheduled ADW scale up during workday business hours (you need ADW's OCID which you can get from OCI Console)
/home/opc/oci-focus-reports/other_scripts/scale_up_db.sh
Wait a couple of minutes for scale up to complete
/home/opc/oci-focus-reports/other_scripts/scale_down_db.sh

Install crontab entries:
/home/opc/oci-focus-reports/other_scripts/install_cron.sh

<!--Login to workpasce OCI_FOCUS_REPORTS with usenrname OCI_FOCUS_REPORT and password provided during resource manager deployment.
For APEX Authentication:
Click on Administration Icon (screenshot) on top right (right to the username) => Manage Users and Group
    Create Groups: ADMINS, CONTRIBUTORS, READERS
    Create at least one User and assing it to group ADMINS-->

1st time Login to OV APEX app:
Username: OVADMIN
Password: Mypassword123123 
You will be prompeted to change the password upon first login

Fof OCI IAM Domains SSO Authentication:
Login to OCI Console -> Identity & Security -> Domains -> Default Domain(Under root Compartment) -> Integrated Application -> OAuth configuration -> Make a note of "Client ID" and "Secret". On the same page click "Edit OAuth configuration" => Redirect URL: https://<<adw_url>/ords/apex_authentication.callback and Post-logout redirect URL: https://<<adw_url>/ords/f?p=100 
Also make a note of the OCI IAM Domain URL in OCI Console -> Identity & Security -> Domains -> Default Domain -> Details -> "Domain URL"

Inside OCI IAM Domains under Default Domain, make sure that the application's admin users are added in Group CA_APEX_ADMINS and all others in CA_APEX_USERS.

Login to APEX app OCI_FOCUS_REPORTS => https://<<adw_url>>/ords/r/apex => OCI_FOCUS_REPORTS with usenrname OCI_FOCUS_REPORT and password provided during resource manager deployment
Click on "Workspace Utilities" => "Web Credentials" and edit OCI OAuth Credentials (Client ID & Secret) with the values taken above.
Then from "App Builder" => Select "Focus Cost Reporting" => "Shared Components" => "Authentication Schemes" => "OCI IAM OAuth" and edit "Discrovery URL" with the URL taken above + Click on "Make Current Scheme" button.
Back to "Shared Components" => "Authorization Schemes" => "Administration Rights" => Edit "Scheme Type" => "Exists SQL Query" => SQL Query =>
select 1 from APEX_WORKSPACE_SESSION_GROUPS
where apex_session_id = :app_session
and group_name in ('CA_APEX_ADMINS')
Same for "Contribution Rights" but with different SQL:
select 1 from APEX_WORKSPACE_SESSION_GROUPS
where apex_session_id = :app_session
and group_name in ('CA_APEX_ADMINS')





<!--Edit Page 1, Page Item P1_CURRENCY and modify its computation to the desired default currency (EUR as an example) (Screenshot)-->
Login to App -> Edit tables -> Edit "Current Active Orders" -> For each order row, update Order Name and give it a friendly name -> Save
Login to App -> Edit tables -> Workloads -> Add Workload -> Select required details and submit. Basically here we create the differenet workloads, environments, customers, sub customers. For cost Analysis we can group compartments together so that it represents a workload or an environment or a customer.
Once all workloads are added, click on "Refresh DB Tables"

Edit Page 2 (OVBot) and edit P2_SQL_AGENT_ID to the OCID of the Endpoint of SQL Agent ID Created (cat /home/opc/gen_ai_agent_endpoint_id.txt or through OCI Console)
On the same page, edit P2_REGION to the region your GenAI inference endpoint will be used (https://docs.oracle.com/en-us/iaas/Content/generative-ai/overview.htm#regions) and the comparment OCID where ObserVantage deployment is configured

<!--Initial Load:
Login to VM:
Edit config.json:
"use_dynamic_prefix": true -> "use_dynamic_prefix": false

After Initial Load:
"use_dynamic_prefix": false -> "use_dynamic_prefix": true
Run all python scripts in /home/opc/oci-focus-reports/python_scripts except compress_old_focus_report_csv.py and oci_exa_maintenance_details.py unless you are an ExaCC/ExaDedicated customer*/

For OVChat:

Create Credentials for focus-reports-user => Create API Key
Go to Workspace Home => Workspace Credentials => Web Credentials => modify ca_user_for_oci and enter details from the API key created above
Got to App => Page 2 => Pre-Rendering => Before Regions => Computations => P6_SQL_AGENT_ID => Static ID => Enter OCID of the newly created Agent Endpoint: ocid1.genaiagentendpoint.oc1.eu-frankfurt-1.amaaaaaaxnbdvtaa5wk2njppjcqa5lpgcqdsumfwaaozb77lkkjn6pd4e3aa 
On the same Page => Computations => P2_COMPARTMENT_ID => The compartment ID the AI Agent is created-->


Cross tenancy policies for Parent - Child organizations (required to get child compartments)
On Parent tenancy, root compartment, define policy like:
define tenancy CHILD as ocid1.tenancy.oc1..123
endorse dynamic-group focus-reports-DG to read all-resources in tenancy CHILD
On Child tenancy, root compartment, define policy like:
define tenancy PARENT as ocid1.tenancy.oc1..123
define dynamic-group focus-reports-DG as ocid1.dynamicgroup.oc1..123 (OCID of dynamic group in PARENT tenancy)
admit dynamic-group focus-reports-DG of tenancy PARENT to read all-resources in tenancy

Then manually create as copy new oci_compartments.py under /home/opc/oci-focus-reports/python_scripts (for example child_compartments.py)
Edit child_compartments.py line 29:
From:
compartment_ocid = config["comp_ocid"]
To:
compartment_ocid = "ocid1.tenancy.oc1..aaaaaaaaqr55dbhrptqbdzghhochnmaarikn6h2chep53nugzd5tygphvemq"

Run it manually and add it in crontab:
crontab -e
30 2 * * * /usr/bin/python /home/opc/oci-focus-reports/python_scripts/child_compartments.py >> /home/opc/oci-focus-reports/logs/child_comps_daily_crontab.log 2>&1
