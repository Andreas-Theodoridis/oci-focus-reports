import os
import re
import json
import base64
import logging
import oracledb
import hashlib
from datetime import datetime
import subprocess

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

# File + console logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logging.info("🚀 Starting DB object comparison...")

# === Initialize Oracle Client ===
oracledb.init_oracle_client(lib_dir=oracle_client_dir)

# === Utility functions ===
def extract_object_ddls(sql_text, object_type):
    ddl_map = {}
    pattern = re.compile(rf'CREATE (?:OR REPLACE )?{object_type}\s+"[^"]+"\."([^"]+)".*?;', re.DOTALL | re.IGNORECASE)
    for match in pattern.finditer(sql_text):
        obj_name = match.group(1).upper()
        ddl_map[obj_name] = match.group(0).strip()
    return ddl_map

def get_secret_value(secret_ocid, signer):
    import oci
    secrets_client = oci.secrets.SecretsClient({}, signer=signer)
    bundle = secrets_client.get_secret_bundle(secret_id=secret_ocid)
    base64_secret = bundle.data.secret_bundle_content.content
    return base64.b64decode(base64_secret).decode("utf-8")

def compare_ddl(script_ddl, db_ddl):
    clean = lambda s: re.sub(r'\s+', ' ', s).strip().lower()
    return clean(script_ddl) == clean(db_ddl)

def get_object_ddl(cursor, object_type, object_name):
    try:
        cursor.execute("""
        BEGIN
            DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'STORAGE', FALSE);
            DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'TABLESPACE', FALSE);
            DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'SEGMENT_ATTRIBUTES', FALSE);
            DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'SQLTERMINATOR', TRUE);
        END;
        """)
        cursor.execute("SELECT DBMS_METADATA.GET_DDL(:1, :2, :3) FROM DUAL", [object_type, object_name, target_schema])
        result = cursor.fetchone()
        return result[0].read() if result and result[0] else None
    except Exception as e:
        logging.warning(f"⚠️ Could not get {object_type} DDL for {object_name}: {e}")
    return None

def get_table_columns(cursor, table_name):
    query = """
    SELECT column_name, data_type, data_length, data_precision, data_scale, nullable
    FROM all_tab_columns
    WHERE table_name = :1 AND owner = :2
    """
    cursor.execute(query, [table_name.upper(), target_schema.upper()])
    return {row[0].upper(): row[1:] for row in cursor.fetchall()}

def parse_columns_from_script(ddl):
    inside = ddl.split("(", 1)[1].rsplit(")", 1)[0]
    lines = [line.strip() for line in inside.split(',')]
    columns = {}
    for line in lines:
        if re.match(r'^(CONSTRAINT|PRIMARY|UNIQUE|FOREIGN|CHECK|PARTITION|USING|ENABLE|DISABLE)', line, re.IGNORECASE):
            continue
        match = re.match(r'^"([^"]+)"\s+(.+)', line)
        if match:
            col = match.group(1).strip()
            col_def = match.group(2).strip()
            columns[col.upper()] = col_def
    return columns

def extract_procedure_ddls(sql_text):
    pattern = re.compile(
        r'(CREATE(?: OR REPLACE)? PROCEDURE\b.*?^\s*/\s*$)',
        re.DOTALL | re.IGNORECASE | re.MULTILINE
    )
    return [match.group(1).strip() for match in pattern.finditer(sql_text)]

def extract_function_ddls(sql_text):
    pattern = re.compile(
        r'(CREATE(?: OR REPLACE)? FUNCTION\b.*?^\s*/\s*$)',
        re.DOTALL | re.IGNORECASE | re.MULTILINE
    )
    return [match.group(1).strip() for match in pattern.finditer(sql_text)]

def extract_insert_statements(sql_text, target_tables):
    inserts = {tbl: [] for tbl in target_tables}
    lines = sql_text.splitlines()
    collecting = False
    buffer = []
    current_table = None

    for line in lines:
        stripped = line.strip()

        # Check for start of INSERT
        if not collecting and stripped.upper().startswith("INSERT INTO"):
            for tbl in target_tables:
                pattern = re.compile(rf'INSERT\s+INTO\s+(?:"[^"]+"\.)?"?{tbl}"?', re.IGNORECASE)
                if pattern.search(stripped):
                    collecting = True
                    current_table = tbl
                    buffer = [line]
                    break
        elif collecting:
            buffer.append(line)
            # Check if line ends with );
            if stripped.endswith(");"):
                inserts[current_table].append("\n".join(buffer).strip())
                collecting = False
                buffer = []
                current_table = None

    return inserts

def execute_sql_script(script_path, user, password, dsn, description):
    logging.info(f"▶️ Executing {description}...")
    sqlplus_cmd = f'sqlplus -s {user}/{password}@{dsn} @{script_path}'
    try:
        result = subprocess.run(sqlplus_cmd, shell=True, check=True, text=True, capture_output=True)
        logging.info(f"✅ {description} executed successfully.")
        logging.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Error while executing {description}:")
        logging.error(e.stderr)

def extract_drop_statements(sql_text):
    pattern = re.compile(
        r'(?i)\bDROP\s+(TABLE|INDEX|VIEW|MATERIALIZED\s+VIEW)\s+(?:"[^"]+"\.)?"[^";\s]+"\s*(CASCADE\s+CONSTRAINTS)?\s*;',
        re.IGNORECASE
    )
    return [match.group(0).strip() for match in pattern.finditer(sql_text)]

def file_checksum(path):
    hash_sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

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

    # === Open patch file (must come before using patch_file) ===
    patch_path = os.path.join(app_dir, "db_scripts", "patch.sql")
    patch_file = open(patch_path, "w")

    # === Extract and write DROP statements from script ===
    drop_statements = extract_drop_statements(sql_text)
    if drop_statements:
        logging.info(f"🗑️ Found {len(drop_statements)} DROP statements in the script.")
        patch_file.write("-- DROP statements from script\n")
        for stmt in drop_statements:
            drop_match = re.match(
                r'(?i)\bDROP\s+(TABLE|INDEX|VIEW|MATERIALIZED\s+VIEW)\s+(?:"[^"]+"\.)?"([^"]+)"', stmt
            )
            if drop_match:
                obj_type = drop_match.group(1).upper().replace("MATERIALIZED VIEW", "MATERIALIZED_VIEW")
                obj_name = drop_match.group(2).upper()
                cursor.execute("""
                    SELECT 1 FROM all_objects
                    WHERE object_type = :1 AND object_name = :2 AND owner = :3
                """, [obj_type, obj_name, target_schema.upper()])
                if cursor.fetchone():
                    logging.info(f"  ✅ Object exists, keeping DROP: {stmt}")
                    patch_file.write(stmt + "\n")
                else:
                    logging.info(f"  ❌ Object not found, skipping DROP: {stmt}")
        patch_file.write("\n")

    # === Extract objects from script ===
    tables = extract_object_ddls(sql_text, "TABLE")
    indexes = extract_object_ddls(sql_text, "INDEX")
    mvs = extract_object_ddls(sql_text, "MATERIALIZED VIEW")
    views = extract_object_ddls(sql_text, "VIEW")

    os.environ['TNS_ADMIN'] = wallet_path
    conn = oracledb.connect(user=db_user, password=db_pass, dsn=db_dsn)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT object_name, object_type FROM all_objects
    WHERE owner = :1 AND object_type IN ('TABLE', 'INDEX', 'MATERIALIZED VIEW', 'VIEW')
    """, [target_schema])
    existing_objects = {(row[0].upper(), row[1].upper()) for row in cursor.fetchall()}

    # === Tables ===
    for table_name, ddl in tables.items():
        if (table_name, 'TABLE') not in existing_objects:
            patch_file.write(ddl + "\n")
            continue
        db_columns = get_table_columns(cursor, table_name)
        script_columns = parse_columns_from_script(ddl)
        for col, col_def in script_columns.items():
            if col not in db_columns:
                patch_file.write(f'ALTER TABLE "{target_schema}"."{table_name}" ADD ({col} {col_def});\n')
            else:
                db_type = db_columns[col][0]
                if 'VARCHAR2' in col_def.upper():
                    match = re.search(r'VARCHAR2\((\d+)\)', col_def.upper())
                    if match:
                        script_len = int(match.group(1))
                        db_len = db_columns[col][1] or 0
                        if script_len > db_len:
                            patch_file.write(f'ALTER TABLE "{target_schema}"."{table_name}" MODIFY ({col} {col_def});\n')

    # === Indexes ===
    for index_name, ddl in indexes.items():
        db_ddl = get_object_ddl(cursor, "INDEX", index_name)
        if db_ddl is None or not compare_ddl(ddl, db_ddl):
            patch_file.write(f'DROP INDEX "{target_schema}"."{index_name}";\n{ddl}\n')

    # === Materialized Views ===
    for mv_name, ddl in mvs.items():
        db_ddl = get_object_ddl(cursor, "MATERIALIZED_VIEW", mv_name)
        if db_ddl is None or not compare_ddl(ddl, db_ddl):
            patch_file.write(f'DROP MATERIALIZED VIEW "{target_schema}"."{mv_name}";\n{ddl}\n')

    # === Procedures & Functions ===
    for proc in extract_procedure_ddls(sql_text):
        patch_file.write(f"{proc}\n/\n\n")

    for func in extract_function_ddls(sql_text):
        patch_file.write(f"{func}\n/\n\n")

    # === Inserts for AI tables ===
    target_insert_tables = ["AI_PROMPT_COMPONENTS", "AI_PROMPT_EXAMPLES"]
    inserts = extract_insert_statements(sql_text, target_insert_tables)
    for table, stmts in inserts.items():
        if stmts:
            patch_file.write(f'TRUNCATE TABLE "{target_schema}"."{table}";\n')
            for stmt in stmts:
                patch_file.write(f"{stmt}\n")

    # === Execute selected procedures at the end ===
    procedures_to_run = [
        "PAGE1_CONS_WRKLD_MONTH_CHART_DATA_PROC",
        "PAGE1_CONS_WRKLD_WEEK_CHART_DATA_PROC",
        "REFRESH_COST_USAGE_TS_PROC",
        "REFRESH_CREDIT_USAGE_AGG_PROC",
        "REFRESH_CREDIT_CONSUMPTION_STATE_PROC",
        "UPDATE_OCI_SUBSCRIPTION_DETAILS",
        "POPULATE_RESOURCE_RELATIONSHIPS_PROC",
        "POPULATE_OKE_RELATIONSHIPS_PROC"
    ]

    patch_file.write("-- Execute procedures\n")
    for proc in procedures_to_run:
        patch_file.write(f"BEGIN {proc}; END;\n/\n")
    patch_file.write("\n")

    patch_file.write("COMMIT;\nEXIT;\n")
    patch_file.close()
    cursor.close()
    conn.close()
    logging.info("✅ Patch file written to db_scripts/patch.sql")

    # === Execute patch.sql if user agrees ===
    if input("❓ Do you want to apply patch.sql to the database? (y/N): ").strip().lower() == 'y':
        execute_sql_script(patch_path, db_user, db_pass, db_dsn, "patch.sql")

    # === Execute install_ov_apex_app.sql if file has changed and user agrees ===
    apex_path = os.path.join(app_dir, "db_scripts", "install_ov_apex_app.sql")
    checksum_path = os.path.join(app_dir, "db_scripts", ".apex_app_checksum")
    current_checksum = file_checksum(apex_path)

    previous_checksum = None
    if os.path.exists(checksum_path):
        with open(checksum_path, "r") as f:
            previous_checksum = f.read().strip()

    if current_checksum != previous_checksum:
        print("🔍 Detected change in install_ov_apex_app.sql.")
        if input("❓ Do you want to install/update APEX app? (y/N): ").strip().lower() == 'y':
            execute_sql_script(apex_path, db_user, db_pass, db_dsn, "install_ov_apex_app.sql")
            with open(checksum_path, "w") as f:
                f.write(current_checksum)
    else:
        print("✅ No changes detected in install_ov_apex_app.sql. Skipping APEX install.")

if __name__ == "__main__":
    main()