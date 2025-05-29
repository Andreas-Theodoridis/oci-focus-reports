import oci
import os
import time
import csv
import json
import base64
import oracledb
import logging
import fnmatch
import shutil
import gzip
from datetime import datetime, timedelta, timezone
from oci.pagination import list_call_get_all_results

app_dir = "/home/opc/oci-focus-reports"

# Load config
config_dir = os.path.join(app_dir, "config")
with open(os.path.join(config_dir, f"config.json")) as f:
    config = json.load(f)

regions = config["regions"]
days_back = config["days_back"]
metric_groups = config["metric_groups"]
app_dir = config["app_dir"]
log_file_pattern= config["availability_reports_file_name_pattern"]

availability_metrics_table = config["availability_metrics_table"]
db_user = config["db_user"]
db_pass = config["db_password"]
db_dsn = config["db_dsn"]
wallet_path = config["wallet_dir"]
use_test_creds = config.get("use_test_credentials", False)

# Logging setup
LOG_DIR = os.path.join(app_dir, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
# Create timestamped log filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(LOG_DIR, f"availability_reports_{timestamp}.log")
latest_log_symlink = os.path.join(LOG_DIR, "latest_availability.log")
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
os.symlink(f"availability_reports_{timestamp}.log", latest_log_symlink)

# Setup logging
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# 💡 Initialize Oracle Thick Client
oracledb.init_oracle_client(lib_dir=config["oracle_client_lib_dir"])

# Define output directory
output_dir = os.path.join(app_dir, "data", "availability")
os.makedirs(output_dir, exist_ok=True)

start_time = datetime.now(timezone.utc) - timedelta(days=days_back)
end_time = datetime.now(timezone.utc)

# Use instance principal signer
signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
identity_client = oci.identity.IdentityClient({}, signer=signer)
tenancy_id = signer.tenancy_id

def get_secret_value(secret_ocid, signer):
    secrets_client = oci.secrets.SecretsClient({}, signer=signer)
    bundle = secrets_client.get_secret_bundle(secret_id=secret_ocid)
    base64_secret = bundle.data.secret_bundle_content.content
    return base64.b64decode(base64_secret).decode("utf-8")

def get_all_compartments():
    logging.info("🔄 Fetching compartments...")
    response = identity_client.list_compartments(
        tenancy_id,
        compartment_id_in_subtree=True,
        access_level="ANY"
    )
    return [c for c in response.data if c.lifecycle_state == 'ACTIVE']

def metrics_exist(monitoring_client, compartment_id, namespace, metrics):
    for metric in metrics:
        try:
            response = monitoring_client.list_metrics(
                compartment_id=compartment_id,
                list_metrics_details=oci.monitoring.models.ListMetricsDetails(
                    namespace=namespace,
                    name=metric
                )
            )
            if not response.data:
                logging.error(f"[❌ Metric Not Found] {metric} in {compartment_id}")
                return False
        except oci.exceptions.ServiceError as e:
            logging.error(f"[ERROR] ListMetrics: {e.message}")
            return False
    return True

def get_metric_data(monitoring_client, compartment, namespace, metric_name, display_keys, csv_rows):
    try:
        query_details = oci.monitoring.models.SummarizeMetricsDataDetails(
            namespace=namespace,
            query=f"{metric_name}[1h].mean()",
            start_time=start_time,
            end_time=end_time
        )

        response = list_call_get_all_results(
            monitoring_client.summarize_metrics_data,
            summarize_metrics_data_details=query_details,
            compartment_id=compartment.id
        )

        for item in response.data:
            display_name = next((item.dimensions.get(k) for k in display_keys if k in item.dimensions), "N/A")

            for dp in item.aggregated_datapoints:
                csv_rows.append({
                    "resourceDisplayName": display_name,
                    "timestamp": dp.timestamp.isoformat(),
                    "namespace": namespace,
                    "compartment_id": compartment.id,
                    "metric_name": metric_name,
                    "value": dp.value
                })
    except oci.exceptions.ServiceError as e:
        logging.error(f"[ERROR] SummarizeMetrics {compartment.name}: {e.message}")

def upload_csv_to_oracle(csv_file, db_user, db_pass, db_dsn):
    df_rows = []
    with open(csv_file, newline="") as f:
        reader = csv.DictReader(f)
        df_rows = [row for row in reader]

    if not df_rows:
        logging.info("⚠️ No data to upload.")
        return

    os.environ['TNS_ADMIN'] = wallet_path
    conn = oracledb.connect(
        user=db_user,
        password=db_pass,
        dsn=db_dsn
    )
    cursor = conn.cursor()
    cursor.execute("ALTER SESSION DISABLE PARALLEL DML")

    table_name = availability_metrics_table
    merge_sql = f"""
    MERGE INTO {table_name} tgt
    USING (
        SELECT :1 AS resourceDisplayName, :2 AS timestamp_str, :3 AS namespace,
            :4 AS compartment_id, :5 AS metric_name, :6 AS value
        FROM dual
    ) src
    ON (
        tgt.resourceDisplayName = src.resourceDisplayName AND
        tgt.timestamp = TO_TIMESTAMP_TZ(src.timestamp_str, 'YYYY-MM-DD"T"HH24:MI:SS.FF3TZH:TZM') AND
        tgt.metric_name = src.metric_name
    )
    WHEN MATCHED THEN UPDATE SET
        tgt.namespace = src.namespace,
        tgt.compartment_id = src.compartment_id,
        tgt.value = src.value  -- ✅ do NOT update tgt.metric_name
    WHEN NOT MATCHED THEN INSERT (
        resourceDisplayName, timestamp, namespace,
        compartment_id, metric_name, value
    )
    VALUES (
        src.resourceDisplayName,
        TO_TIMESTAMP_TZ(src.timestamp_str, 'YYYY-MM-DD"T"HH24:MI:SS.FF3TZH:TZM'),
        src.namespace, src.compartment_id, src.metric_name, src.value
    )
    """

    logging.info(f"⬆️ Uploading {len(df_rows)} rows to {table_name}...")
    data = []
    for row in df_rows:
        try:
            value = float(row["value"])
            data.append((
                row["resourceDisplayName"],
                row["timestamp"],
                row["namespace"],
                row["compartment_id"],
                row["metric_name"].strip().lower(),
                value
            ))
        except (ValueError, TypeError) as e:
            logging.warning(f"❌ Skipping row due to conversion error: {row} → {e}")

    cursor.executemany(merge_sql, data)
    conn.commit()
    cursor.close()
    conn.close()
    logging.info("✅ Upload complete.")

def main():
    if use_test_creds:
        db_user = config["test_credentials"]["user"]
        db_pass = config["test_credentials"]["password"]
        db_dsn = config["test_credentials"]["dsn"]
    else:
        db_conf = config["db_credentials"]
        db_user = config["db_credentials"]["user"]
        db_pass = get_secret_value(db_conf["pass_secret_ocid"], signer)
        db_dsn = config["db_credentials"]["dsn"]

    compartments = get_all_compartments()

    for region in regions:
        logging.info(f"\n🌍 Region: {region}")
        monitoring_client = oci.monitoring.MonitoringClient({}, signer=signer)
        monitoring_client.base_client.set_region(region)

        for group in metric_groups:
            logging.info(f"\n📊 Namespace: {group['namespace']}")
            rows = []

            for compartment in compartments:
                if metrics_exist(monitoring_client, compartment.id, group["namespace"], group["metrics"]):
                    for metric in group["metrics"]:
                        logging.info(f"📦 {compartment.name} → {metric}")
                        get_metric_data(monitoring_client, compartment, group["namespace"], metric, group["resource_display_key"], rows)
                        time.sleep(0.4)
                time.sleep(0.1)

            # Use os.path.join to create full path
            output_path = os.path.join(output_dir, group["output_file"])
            csv_file = group["output_file"]
            with open(output_path, "w", newline="") as f:
                fieldnames = ["resourceDisplayName", "timestamp", "namespace", "compartment_id", "metric_name", "value"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            logging.info(f"✅ {output_path} written with {len(rows)} rows.")
            upload_csv_to_oracle(output_path, db_user, db_pass, db_dsn)

if __name__ == "__main__":
    main()
