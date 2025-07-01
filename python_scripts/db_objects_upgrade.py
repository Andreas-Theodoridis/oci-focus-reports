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

# === Main ===
def main():
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
        elif not compare_ddl(ddl, db_ddl):
            logging.warning(f"✏️ Table {table_name}: Differs from DB → SHOULD ALTER")
        else:
            logging.info(f"✅ Table {table_name}: Matches")

    cursor.close()
    conn.close()
    logging.info("✅ Comparison completed.")

if __name__ == "__main__":
    main()