import os
import re
import json
import base64
import logging
import oracledb
from datetime import datetime

# === Load config ===
app_dir = "/home/opc/oci-focus-reports"
config_path = os.path.join(app_dir, "config", "config.json")
with open(config_path) as f:
    config = json.load(f)

wallet_path = config["wallet_dir"]
db_user = config["db_user"]
db_pass = config["db_password"]
db_dsn = config["db_dsn"]
oracle_client_dir = config["oracle_client_lib_dir"]
sql_file_path = os.path.join(app_dir, "db_scripts", "install_ov_db_objects.sql")
target_schema = "OCI_FOCUS_REPORTS"

# === Logging setup ===
log_dir = os.path.join(app_dir, "logs")
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(log_dir, f"compare_db_objects_{timestamp}.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logging.info("🚀 Starting DB object comparison...")

# === Initialize Oracle Client ===
oracledb.init_oracle_client(lib_dir=oracle_client_dir)

# === Extract CREATE TABLE DDLs ===
def extract_table_ddls(sql_text):
    table_ddls = {}
    pattern = re.compile(r'CREATE TABLE\s+"([^"]+)"\."([^"]+)"\s*\((.*?)\)\s*DEFAULT COLLATION.*?;', re.DOTALL | re.IGNORECASE)
    for match in pattern.finditer(sql_text):
        schema, table, cols = match.groups()
        ddl = match.group(0)
        table_ddls[table.upper()] = ddl.strip()
    return table_ddls

# === Fetch existing DB DDL using DBMS_METADATA ===
def get_existing_ddl(cursor, table_name):
    try:
        plsql = """
        BEGIN
            DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'STORAGE', FALSE);
            DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'TABLESPACE', FALSE);
            DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'SEGMENT_ATTRIBUTES', FALSE);
            DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'SQLTERMINATOR', TRUE);
        END;
        """
        cursor.execute(plsql)

        cursor.execute("SELECT DBMS_METADATA.GET_DDL('TABLE', :1, :2) FROM DUAL", [table_name, target_schema])
        result = cursor.fetchone()
        if result and result[0]:
            return result[0].read()
    except Exception as e:
        logging.warning(f"⚠️ Could not get DDL for {table_name}: {e}")
    return None

# === Compare two DDL strings (normalized) ===
def compare_ddl(script_ddl, db_ddl):
    clean = lambda s: re.sub(r'\s+', ' ', s).strip().lower()
    return clean(script_ddl) == clean(db_ddl)

def get_secret_value(secret_ocid, signer):
    import oci
    secrets_client = oci.secrets.SecretsClient({}, signer=signer)
    bundle = secrets_client.get_secret_bundle(secret_id=secret_ocid)
    base64_secret = bundle.data.secret_bundle_content.content
    return base64.b64decode(base64_secret).decode("utf-8")

# === Main ===
def main():
    import oci
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()

    if config.get("use_test_credentials", False):
        db_user = config["test_credentials"]["user"]
        db_pass = config["test_credentials"]["password"]
        db_dsn = config["test_credentials"]["dsn"]
    else:
        db_conf = config["db_credentials"]
        db_user = db_conf["user"]
        db_pass = get_secret_value(db_conf["pass_secret_ocid"], signer)
        db_dsn = db_conf["dsn"]

    with open(sql_file_path, 'r') as f:
        sql_text = f.read()
    defined_tables = extract_table_ddls(sql_text)
    logging.info(f"📋 Found {len(defined_tables)} tables in SQL script.")

    os.environ['TNS_ADMIN'] = wallet_path
    conn = oracledb.connect(user=db_user, password=db_pass, dsn=db_dsn)
    cursor = conn.cursor()

    for table_name, ddl in defined_tables.items():
        db_ddl = get_existing_ddl(cursor, table_name)

        if db_ddl is None:
            logging.info(f"➕ Table {table_name}: Not found in DB → SHOULD CREATE")
            print(f"\n--- {table_name} (MISSING IN DB) ---")
            print(ddl)
        elif not compare_ddl(ddl, db_ddl):
            logging.warning(f"✏️ Table {table_name}: Differs from DB → SHOULD ALTER")
            print(f"\n--- {table_name} (DIFFERENCE FOUND) ---")
            print("▶️ Script DDL:\n", ddl)
            print("\n🔁 DB DDL:\n", db_ddl)
        else:
            logging.info(f"✅ Table {table_name}: Matches")

    cursor.close()
    conn.close()
    logging.info("✅ Comparison completed.")

if __name__ == "__main__":
    main()