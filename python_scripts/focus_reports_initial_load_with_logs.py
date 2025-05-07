import os
import gzip
import shutil
import logging
import oci
import csv
import json
import oracledb
import fnmatch
from datetime import datetime, timedelta

app_dir = "/home/opc/oci-focus-reports"

# Load config
config_dir = os.path.join(app_dir, "config")
with open(os.path.join(config_dir, f"metrics_config.json")) as f:
    config = json.load(f)

rep_namespace = config["reporting_namespace"]
rep_bucket = config["reporting_bucket"]
dest_path = os.path.join(app_dir, "data", "fc")
app_dir = config["app_dir"]
log_file_pattern= config["focus_reports_initial_file_name_pattern"]
prefix = config["prefix_file"]

#Load DB Config
dbconfig_dir = os.path.join(app_dir, "config")
with open(os.path.join(dbconfig_dir, f"db_config.json")) as df:
    dbconfig = json.load(df)

focus_reports_table = dbconfig["focus_reports_table"]
db_user = dbconfig["db_user"]
db_pass = dbconfig["db_password"]
db_dsn = dbconfig["db_dsn"]
wallet_path = dbconfig["wallet_dir"]

# Logging setup
LOG_DIR = os.path.join(app_dir, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
# Create timestamped log filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(LOG_DIR, f"focus_reports_initial_load.log")
latest_log_symlink = os.path.join(LOG_DIR, "latest_initial_load.log")
# Zip all previous .log files (except current one)
for filename in os.listdir(LOG_DIR):
    if fnmatch.fnmatch(filename, log_file_pattern) and filename != os.path.basename(log_filename):
        full_path = os.path.join(LOG_DIR, filename)
        gz_path = full_path + '.gz'
        with open(full_path, 'rb') as f_in, gzip.open(gz_path, 'wb') as f_out:
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

# Update 'latest.log' symlink
if os.path.exists(latest_log_symlink) or os.path.islink(latest_log_symlink):
    os.remove(latest_log_symlink)
os.symlink(f"focus_reports_initial_load.log", latest_log_symlink)

# Setup logging
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# 💡 Initialize Oracle Thick Client
oracledb.init_oracle_client(lib_dir=dbconfig["oracle_client_lib_dir"])

# Date parsing helper
def try_parse_datetime(val, formats):
    for fmt in formats:
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            continue
    return None

# Preprocess each CSV row
def preprocess_row(header, row):
    new_row = []
    for col, val in zip(header, row):
        col = col.upper()
        val = val.strip()

        if not val:
            new_row.append(None)
            continue

        if col in ['BILLINGPERIODEND', 'BILLINGPERIODSTART']:
            dt = try_parse_datetime(val, ["%Y-%m-%dT%H:%M:%S.%fZ"])
            new_row.append(dt)
        elif col in ['CHARGEPERIODEND', 'CHARGEPERIODSTART']:
            dt = try_parse_datetime(val, [
                "%Y-%m-%dT%H:%MZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ])
            new_row.append(dt)
        else:
            new_row.append(val)
    return new_row

# Insert CSV data into DB
def insert_csv_into_db(csv_path, connection, batch_size=1000):
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = [h.strip().upper() for h in next(reader)]

        cursor = connection.cursor()
        placeholders = ', '.join([f':{i+1}' for i in range(len(header))])
        columns = ', '.join(f'"{col}"' for col in header)

        insert_sql = f"""
            INSERT INTO {focus_reports_table}
            ({columns}) VALUES ({placeholders})
        """

        batch = []
        inserted_count = 0

        for row in reader:
            if not any(row):
                continue
            batch.append(preprocess_row(header, row))

            if len(batch) >= batch_size:
                try:
                    cursor.executemany(insert_sql, batch)
                    inserted_count += len(batch)
                    batch.clear()
                except Exception as e:
                    logging.error(f"❌ Batch insert failed\n{e}")
                    batch.clear()

        if batch:
            try:
                cursor.executemany(insert_sql, batch)
                inserted_count += len(batch)
            except Exception as e:
                logging.error(f"❌ Final batch insert failed\n{e}")

        connection.commit()
        cursor.close()
        logging.info(f"✅ Inserted rows from {os.path.basename(csv_path)}: {inserted_count}")

# Main function
def download_extract_and_insert():
    try:
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        object_storage = oci.object_storage.ObjectStorageClient(config={}, signer=signer)

        report_bucket_objects = oci.pagination.list_call_get_all_results(
            object_storage.list_objects,
            namespace_name=rep_namespace,
            bucket_name=rep_bucket,
            prefix=prefix
        )

        os.environ['TNS_ADMIN'] = wallet_path
        with oracledb.connect(user=db_user, password=db_pass, dsn=db_dsn) as conn:
            for obj in report_bucket_objects.data.objects:
                local_gz_path = os.path.join(dest_path, obj.name)
                extracted_path = local_gz_path.rstrip('.gz')

                os.makedirs(os.path.dirname(local_gz_path), exist_ok=True)

                # Download .gz
                response = object_storage.get_object(rep_namespace, rep_bucket, obj.name)
                with open(local_gz_path, 'wb') as f:
                    for chunk in response.data.raw.stream(1024 * 1024, decode_content=False):
                        f.write(chunk)
                logging.info(f"📥 Downloaded: {obj.name}")

                # Extract
                with gzip.open(local_gz_path, 'rb') as gz_file:
                    with open(extracted_path, 'wb') as out_file:
                        shutil.copyfileobj(gz_file, out_file)
                logging.info(f"📂 Extracted to: {extracted_path}")

                os.remove(local_gz_path)

                # Insert
                insert_csv_into_db(extracted_path, conn)

                #os.remove(extracted_path)
                logging.info(f"✅ Finished processing: {extracted_path}")

    except Exception as e:
        logging.error(f"Error processing reports: {str(e)}")

if __name__ == "__main__":
    download_extract_and_insert()
