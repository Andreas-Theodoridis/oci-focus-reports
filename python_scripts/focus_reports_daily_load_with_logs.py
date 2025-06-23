import os
import gzip
import shutil
import logging
import oci
import csv
import json
import oracledb
import fnmatch
import base64
from datetime import datetime, timedelta, timezone

app_dir = "/home/opc/oci-focus-reports"

# Load config
config_dir = os.path.join(app_dir, "config")
with open(os.path.join(config_dir, "config.json")) as f:
    config = json.load(f)

rep_namespace = config["reporting_namespace"]
rep_bucket = config["reporting_bucket"]
dest_path = os.path.join(app_dir, "data", "fc")
app_dir = config["app_dir"]
log_file_pattern = config["focus_reports_file_name_pattern"]

focus_reports_table = config["focus_reports_table"]
db_user = config["db_user"]
db_pass = config["db_password"]
db_dsn = config["db_dsn"]
wallet_path = config["wallet_dir"]

# Logging setup
LOG_DIR = os.path.join(app_dir, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(LOG_DIR, f"focus_reports_{timestamp}.log")
latest_log_symlink = os.path.join(LOG_DIR, "latest.log")

# Zip old log files
for filename in os.listdir(LOG_DIR):
    if fnmatch.fnmatch(filename, log_file_pattern) and filename != os.path.basename(log_filename):
        full_path = os.path.join(LOG_DIR, filename)
        gz_path = full_path + ".gz"
        with open(full_path, "rb") as f_in, gzip.open(gz_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.remove(full_path)

# Delete .gz logs older than 30 days
cutoff_date = datetime.now() - timedelta(days=30)
for filename in os.listdir(LOG_DIR):
    if filename.endswith(".gz"):
        full_path = os.path.join(LOG_DIR, filename)
        mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
        if mtime < cutoff_date:
            os.remove(full_path)

# Update latest log symlink
if os.path.exists(latest_log_symlink) or os.path.islink(latest_log_symlink):
    os.remove(latest_log_symlink)
os.symlink(f"focus_reports_{timestamp}.log", latest_log_symlink)

# Setup logging
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Initialize Oracle Thick Client
oracledb.init_oracle_client(lib_dir=config["oracle_client_lib_dir"])

# Ensure local destination path exists
os.makedirs(dest_path, exist_ok=True)

def try_parse_datetime(val, formats):
    for fmt in formats:
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            continue
    return None

def preprocess_row(header, row):
    new_row = []
    for col, val in zip(header, row):
        col = col.upper()
        val = val.strip()
        if not val:
            new_row.append(None)
            continue
        if col in ["BILLINGPERIODEND", "BILLINGPERIODSTART"]:
            dt = try_parse_datetime(val, ["%Y-%m-%dT%H:%M:%S.%fZ"])
            new_row.append(dt)
        elif col in ["CHARGEPERIODEND", "CHARGEPERIODSTART"]:
            dt = try_parse_datetime(val, [
                "%Y-%m-%dT%H:%MZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ])
            new_row.append(dt)
        else:
            new_row.append(val)
    return new_row

def log_and_execute(cursor, sql, params=None):
    if params:
        logging.info(f"➡️ Executing SQL:\n{sql}\nWith params: {params}")
        cursor.execute(sql, params)
    else:
        logging.info(f"➡️ Executing SQL:\n{sql}")
        cursor.execute(sql)

def merge_csv_into_db(csv_path, connection, batch_size=1000):
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = [h.strip().upper() for h in next(reader)]
        if "OCI_REFERENCENUMBER" not in header:
            logging.error(f"❌ Missing required column 'OCI_REFERENCENUMBER' in {csv_path}")
            return
        cursor = connection.cursor()
        batch = []
        merged_count = 0
        for row in reader:
            if not any(row):
                continue
            batch.append(preprocess_row(header, row))
            if len(batch) >= batch_size:
                merged_count += execute_merge_batch(cursor, header, batch)
                batch.clear()
        if batch:
            merged_count += execute_merge_batch(cursor, header, batch)
        connection.commit()
        cursor.close()
        logging.info(f"✅ Merged rows from {os.path.basename(csv_path)}: {merged_count}")

def execute_merge_batch(cursor, header, batch):
    merged = 0
    try:
        for row in batch:
            insert_values = ", ".join([f":{i+1}" for i in range(len(header))])
            columns = ", ".join(f'"{col}"' for col in header)
            updates = ", ".join([f'target."{col}" = :{i+1}' for i, col in enumerate(header) if col != "OCI_REFERENCENUMBER"])
            source_alias = ", ".join([f":{i+1} AS \"{col}\"" for i, col in enumerate(header)])
            merge_sql = f"""
                MERGE INTO {focus_reports_table} target
                USING (SELECT {source_alias} FROM dual) source
                ON (target."OCI_REFERENCENUMBER" = source."OCI_REFERENCENUMBER")
                WHEN MATCHED THEN UPDATE SET {updates}
                WHEN NOT MATCHED THEN INSERT ({columns}) VALUES ({insert_values})
            """
            cursor.execute(merge_sql, row)
            merged += 1
    except Exception as e:
        logging.error(f"❌ Merge failed for batch: {e}")
    return merged

def get_secret_value(secret_ocid, signer):
    secret_client = oci.secrets.SecretsClient(config={}, signer=signer)
    response = secret_client.get_secret_bundle(secret_id=secret_ocid)
    base64_secret = response.data.secret_bundle_content.content
    secret_value = base64.b64decode(base64_secret).decode("utf-8")
    return secret_value

def download_extract_and_insert():
    try:
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        object_storage = oci.object_storage.ObjectStorageClient(config={}, signer=signer)

        # Fetch secret dynamically from Vault if specified
        db_password = db_pass
        if "pass_secret_ocid" in config.get("db_credentials", {}):
            db_password = get_secret_value(config["db_credentials"]["pass_secret_ocid"], signer)

        # Determine prefix and cutoff_time dynamically
        if config.get("use_dynamic_prefix", False):
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            base = config.get("prefix_base", "FOCUS Reports")
            prefix = f"{base}/{yesterday.year}/{yesterday.strftime('%m')}/{yesterday.strftime('%d')}"
            cutoff_time = datetime(yesterday.year, yesterday.month, yesterday.day)
        else:
            prefix = config["prefix_file"]
            cutoff_time = None  # No cutoff filtering

        report_bucket_objects = oci.pagination.list_call_get_all_results(
            object_storage.list_objects,
            namespace_name=rep_namespace,
            bucket_name=rep_bucket,
            prefix=prefix,
            fields='timeCreated'
        )

        valid_objects = []
        for obj in report_bucket_objects.data.objects:
            if obj.time_created is None:
                logging.warning(f"⚠️ Skipping object without time_created: {obj.name}")
                continue

            logging.info(f"📦 Found object: {obj.name}, created at {obj.time_created}")

            if not cutoff_time or obj.time_created.replace(tzinfo=None) >= cutoff_time:
                valid_objects.append(obj)
            else:
                logging.info(f"⏩ Skipping object older than cutoff: {obj.name}")

        logging.info(f"✅ Valid objects for processing: {len(valid_objects)}")



        os.environ["TNS_ADMIN"] = wallet_path
        with oracledb.connect(user=db_user, password=db_password, dsn=db_dsn) as conn:
            conn.cursor().execute("ALTER SESSION DISABLE PARALLEL DML")
            for obj in valid_objects:
                local_gz_path = os.path.join(dest_path, obj.name)
                extracted_path = local_gz_path.rstrip(".gz")
                os.makedirs(os.path.dirname(local_gz_path), exist_ok=True)

                response = object_storage.get_object(rep_namespace, rep_bucket, obj.name)
                with open(local_gz_path, "wb") as f:
                    for chunk in response.data.raw.stream(1024 * 1024, decode_content=False):
                        f.write(chunk)
                logging.info(f"📥 Downloaded: {obj.name}")

                with gzip.open(local_gz_path, "rb") as gz_file:
                    with open(extracted_path, "wb") as out_file:
                        shutil.copyfileobj(gz_file, out_file)
                logging.info(f"📂 Extracted to: {extracted_path}")

                os.remove(local_gz_path)
                merge_csv_into_db(extracted_path, conn)
                logging.info(f"✅ Finished processing: {extracted_path}")
                # Post-processing refreshes only once after all files
            with oracledb.connect(user=db_user, password=db_password, dsn=db_dsn) as final_conn:
                final_cursor = final_conn.cursor()
                log_and_execute(final_cursor, "BEGIN PAGE1_CONS_WRKLD_MONTH_CHART_DATA_PROC; END;")
                log_and_execute(final_cursor, "BEGIN PAGE1_CONS_WRKLD_WEEK_CHART_DATA_PROC; END;")
                log_and_execute(final_cursor, "BEGIN REFRESH_COST_USAGE_TS_PROC; END;")
                log_and_execute(final_cursor, "BEGIN DBMS_MVIEW.REFRESH('FILTER_VALUES_MV', METHOD => 'C'); END;")
                final_cursor.close()

    except Exception as e:
        logging.error(f"Error processing reports: {str(e)}")

if __name__ == "__main__":
    download_extract_and_insert()