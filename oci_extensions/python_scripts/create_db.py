import oracledb
import os
import json
import logging
import oci
import base64
from datetime import datetime

app_dir = "/home/opc/oci_extensions"

# Load config
config_dir = os.path.join(app_dir, "config")
with open(os.path.join(config_dir, f"metrics_config.json")) as f:
    config = json.load(f)

log_file_pattern= config["db_scripts_name_pattern"]

#Load DB Config
dbconfig_dir = os.path.join(app_dir, "config")
with open(os.path.join(dbconfig_dir, f"db_config.json")) as df:
    dbconfig = json.load(df)

db_user = dbconfig["db_user"]
db_pass = dbconfig["db_password"]
db_dsn = dbconfig["db_dsn"]
wallet_path = dbconfig["wallet_dir"]
use_test_creds = dbconfig.get("use_test_credentials", False)

# Logging setup
LOG_DIR = os.path.join(app_dir, "logs", "db")
os.makedirs(LOG_DIR, exist_ok=True)
# Create timestamped log filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(LOG_DIR, f"db_{timestamp}.log")

# Setup logging
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# 💡 Initialize Oracle Thick Client
oracledb.init_oracle_client(lib_dir=dbconfig["oracle_client_lib_dir"])

# Use instance principal signer
signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
identity_client = oci.identity.IdentityClient({}, signer=signer)
tenancy_id = signer.tenancy_id

def get_secret_value(secret_ocid, signer):
    secrets_client = oci.secrets.SecretsClient({}, signer=signer)
    bundle = secrets_client.get_secret_bundle(secret_id=secret_ocid)
    base64_secret = bundle.data.secret_bundle_content.content
    return base64.b64decode(base64_secret).decode("utf-8")

# Connection details
if use_test_creds:
    db_user = dbconfig["test_credentials"]["user"]
    db_pass = dbconfig["test_credentials"]["password"]
    db_dsn = dbconfig["test_credentials"]["dsn"]
else:
    db_conf = dbconfig["db_credentials"]
    db_user = dbconfig["db_credentials"]["user"]
    db_pass = get_secret_value(db_conf["pass_secret_ocid"], signer)
    db_dsn = dbconfig["db_credentials"]["dsn"]

# Directory containing your .sql files
sql_dir = os.path.join(app_dir, "db_scripts")

# Connect and execute each .sql file
try:
    os.environ['TNS_ADMIN'] = wallet_path
    with oracledb.connect(user=db_user, password=db_pass, dsn=db_dsn) as conn:
        print("✅ Connected to the database.")

        with conn.cursor() as cursor:
            for sql_file in sorted(sql_dir.glob("*.sql")):
                print(f"📄 Executing: {sql_file.name}")
                with open(sql_file, "r") as file:
                    sql_script = file.read()
                    try:
                        cursor.execute(sql_script)
                        print("✅ Executed successfully.")
                    except oracledb.DatabaseError as err:
                        print(f"❌ Error in {sql_file.name}: {err}")
                        break

except oracledb.Error as e:
    print("❌ Connection failed or error occurred:", e)
