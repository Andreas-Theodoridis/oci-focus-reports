Initial Load:
Edit config.json:
"use_dynamic_prefix": true -> "use_dynamic_prefix": false

After Initial Load:
"use_dynamic_prefix": false -> "use_dynamic_prefix": true

For OVChat:

Create Credentials for focus-reports-user => Create API Key
Go to Workspace Home => Workspace Credentials => Web Credentials => modify ca_user_for_oci and enter details from the API key created above
Got to App => Page 6 => Pre-Rendering => Before Regions => Computations => P6_SQL_AGENT_ID => Static ID => Enter OCID of the newly created Agent Endpoint: ocid1.genaiagentendpoint.oc1.eu-frankfurt-1.amaaaaaaxnbdvtaa5wk2njppjcqa5lpgcqdsumfwaaozb77lkkjn6pd4e3aa 