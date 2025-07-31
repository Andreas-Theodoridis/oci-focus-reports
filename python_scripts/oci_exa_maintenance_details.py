import oci
import csv
import os
import json
import oracledb
import fnmatch
import shutil
import gzip
import logging
import base64
from datetime import datetime, timedelta, timezone

app_dir = "/home/opc/oci-focus-reports"

# Load config
config_dir = os.path.join(app_dir, "config")
with open(os.path.join(config_dir, f"config.json")) as f:
    config = json.load(f)

regions = config["regions"]
app_dir = config["app_dir"]
log_file_pattern= config["exa_maintenance_file_name_pattern"]
exa_maintenance_metrics_table = config["exa_maintenance_metrics_table"]
db_user = config["db_user"]
db_pass = config["db_password"]
db_dsn = config["db_dsn"]
wallet_path = config["wallet_dir"]
use_test_creds = config.get("use_test_credentials", False)

# Logging setup
LOG_DIR = os.path.join(app_dir, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
OLD_LOG_DIR = os.path.join(LOG_DIR, "old")
os.makedirs(OLD_LOG_DIR, exist_ok=True)
# Create timestamped log filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(LOG_DIR, f"exa_maintenance_reports_{timestamp}.log")
latest_log_symlink = os.path.join(LOG_DIR, "latest_exa_maintenance.log")
# Zip old logs
for filename in os.listdir(LOG_DIR):
    if (
        fnmatch.fnmatch(filename, log_file_pattern)
        and filename != os.path.basename(log_filename)
        and not filename.endswith(".gz")
    ):
        full_path = os.path.join(LOG_DIR, filename)
        gz_temp_path = full_path + ".gz"
        final_gz_path = os.path.join(OLD_LOG_DIR, os.path.basename(gz_temp_path))

        with open(full_path, "rb") as f_in, gzip.open(gz_temp_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

        os.remove(full_path)
        shutil.move(gz_temp_path, final_gz_path)
        logging.info(f"📦 Archived log: {final_gz_path}")

# Remove logs older than 30 days
cutoff_date = datetime.now() - timedelta(days=30)
for filename in os.listdir(OLD_LOG_DIR):
    if filename.endswith(".gz"):
        full_path = os.path.join(OLD_LOG_DIR, filename)
        mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
        if mtime < cutoff_date:
            os.remove(full_path)
            logging.info(f"🧹 Deleted old log archive: {filename}")

# Update 'latest.log' symlink
if os.path.exists(latest_log_symlink) or os.path.islink(latest_log_symlink):
    os.remove(latest_log_symlink)
os.symlink(f"exa_maintenance_reports_{timestamp}.log", latest_log_symlink)

# Setup logging
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# 💡 Initialize Oracle Thick Client
oracledb.init_oracle_client(lib_dir=config["oracle_client_lib_dir"])

# Define output directory
output_dir = os.path.join(app_dir, "data", "exa_maintenance")
os.makedirs(output_dir, exist_ok=True)


# -----------------------------------------
# 1. Set up Instance Principal Authentication
# -----------------------------------------
signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
tenancy_id = signer.tenancy_id

# Set your desired regions
#regions = ["eu-frankfurt-1", "uk-london-1"]

# -----------------------------------------
# 2. Discover Compartments with Exadata Infra
# -----------------------------------------
identity_client = oci.identity.IdentityClient(config={}, signer=signer)
compartments_response = oci.pagination.list_call_get_all_results(
    identity_client.list_compartments,
    tenancy_id,
    compartment_id_in_subtree=True,
    access_level="ANY"
)
compartments = compartments_response.data
compartments.append(oci.identity.models.Compartment(id=tenancy_id))  # Add root

exadata_compartments_by_region = {}

for region in regions:
    logging.info(f"\n🔍 Scanning region: {region}")
    db_client = oci.database.DatabaseClient(config={"region": region}, signer=signer)
    exadata_compartments = []

    for comp in compartments:
        try:
            infra_found = False

            # Check for cloud Exadata
            try:
                exadata = db_client.list_exadata_infrastructures(compartment_id=comp.id).data
                if exadata:
                    infra_found = True
            except oci.exceptions.ServiceError as e:
                if e.status != 404:
                    logging.warning(f"⚠️ Error checking cloud Exadata in {comp.id}: {e}")

            # Check for Cloud@Customer Exadata
            try:
                cloud_exadata = db_client.list_cloud_exadata_infrastructures(compartment_id=comp.id).data
                if cloud_exadata:
                    infra_found = True
            except oci.exceptions.ServiceError as e:
                if e.status != 404:
                    logging.warning(f"⚠️ Error checking Cloud@Customer Exadata in {comp.id}: {e}")

            if infra_found:
                logging.info(f"✅ Found Exadata infra in {region}, Compartment: {comp.id}")
                exadata_compartments.append(comp.id)

        except oci.exceptions.ServiceError as e:
            if e.status != 404:
                logging.warning(f"⚠️  Skipping compartment {comp.id}: {e}")

    exadata_compartments_by_region[region] = exadata_compartments

# -----------------------------------------
# 3. Fetch Maintenance Run History & Write CSV
# -----------------------------------------
def fetch_all_maintenance_runs(db_client, compartment_id):
    all_results = []
    response = db_client.list_maintenance_run_history(compartment_id=compartment_id)
    all_results.extend(response.data)

    while response.has_next_page:
        response = db_client.list_maintenance_run_history(
            compartment_id=compartment_id,
            page=response.next_page
        )
        all_results.extend(response.data)

    return all_results

from datetime import datetime

def format_date(date_value):
    if date_value is None:
        return None

    # Handle string input
    if isinstance(date_value, str):
        try:
            # Remove timezone if present
            date_value = date_value.replace('T', ' ').replace('Z', '')
            if '+' in date_value:
                date_value = date_value.split('+')[0]
            try:
                parsed_date = datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                parsed_date = datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S')
            # Format to Oracle-friendly format: 13-Nov-2021 6:54:25 AM
            return parsed_date.strftime('%d-%b-%Y %-I:%M:%S %p')  # Use %#I instead of %-I if on Windows
        except ValueError:
            logging.warning(f"[WARN] Invalid date format: {date_value}")
            return None
    elif isinstance(date_value, datetime):
        return date_value.strftime('%d-%b-%Y %-I:%M:%S %p')  # Use %#I for Windows
    return None

def get_secret_value(secret_ocid, signer):
    secrets_client = oci.secrets.SecretsClient({}, signer=signer)
    bundle = secrets_client.get_secret_bundle(secret_id=secret_ocid)
    base64_secret = bundle.data.secret_bundle_content.content
    return base64.b64decode(base64_secret).decode("utf-8")    

def flatten_run_details(item):
    details = getattr(item, 'maintenance_run_details', {})
    est_patch_time = getattr(details, 'estimated_patching_time', {})

    return {
        "id": getattr(item, 'id', None),
        "compartment_id": getattr(details, 'compartment_id', None),
        "current_custom_action_timeout_in_mins": getattr(details, 'current_custom_action_timeout_in_mins', None),
        "current_patching_component": getattr(details, 'current_patching_component', None),
        "custom_action_timeout_in_mins": getattr(details, 'custom_action_timeout_in_mins', None),
        "database_software_image_id": getattr(details, 'database_software_image_id', None),
        "description": getattr(details, 'description', None),
        "display_name": getattr(details, 'display_name', None),
        "estimated_db_server_patching_time": getattr(est_patch_time, 'estimated_db_server_patching_time', None),
        "estimated_network_switches_patching_time": getattr(est_patch_time, 'estimated_network_switches_patching_time', None),
        "estimated_storage_server_patching_time": getattr(est_patch_time, 'estimated_storage_server_patching_time', None),
        "total_estimated_patching_time": getattr(est_patch_time, 'total_estimated_patching_time', None),
        "is_custom_action_timeout_enabled": getattr(details, 'is_custom_action_timeout_enabled', None),
        "is_dst_file_update_enabled": getattr(details, 'is_dst_file_update_enabled', None),
        "is_maintenance_run_granular": getattr(details, 'is_maintenance_run_granular', None),
        "lifecycle_details": getattr(details, 'lifecycle_details', None),
        "lifecycle_state": getattr(details, 'lifecycle_state', None),
        "maintenance_subtype": getattr(details, 'maintenance_subtype', None),
        "maintenance_type": getattr(details, 'maintenance_type', None),
        "patch_failure_count": getattr(details, 'patch_failure_count', None),
        "patch_id": getattr(details, 'patch_id', None),
        "patching_end_time": format_date(getattr(details, 'patching_end_time', None)),  # Use format_date here
        "patching_mode": getattr(details, 'patching_mode', None),
        "patching_start_time": format_date(getattr(details, 'patching_start_time', None)),  # Use format_date here
        "patching_status": getattr(details, 'patching_status', None),
        "peer_maintenance_run_id": getattr(details, 'peer_maintenance_run_id', None),
        "peer_maintenance_run_ids": getattr(details, 'peer_maintenance_run_ids', None),
        "target_db_server_version": getattr(details, 'target_db_server_version', None),
        "target_resource_id": getattr(details, 'target_resource_id', None),
        "target_resource_type": getattr(details, 'target_resource_type', None),
        "target_storage_server_version": getattr(details, 'target_storage_server_version', None),
        "time_ended": format_date(getattr(details, 'time_ended', None)),
        "time_scheduled": format_date(getattr(details, 'time_scheduled', None)),
        "time_started": format_date(getattr(details, 'time_started', None)),
        "total_time_taken_in_mins": getattr(details, 'total_time_taken_in_mins', None)
    }

all_data = []

for region, compartment_ids in exadata_compartments_by_region.items():
    db_client = oci.database.DatabaseClient(config={"region": region}, signer=signer)
    logging.info(f"\n📦 Fetching maintenance run history in region {region}...")
    for comp_id in compartment_ids:
        try:
            history = fetch_all_maintenance_runs(db_client, comp_id)
            flattened = [flatten_run_details(item) for item in history]
            all_data.extend(flattened)
        except Exception as e:
            logging.warning(f"⚠️ Failed to fetch for compartment {comp_id}: {e}")

csv_file = os.path.join(output_dir, "maintenance_run_history.csv")
fieldnames = list(all_data[0].keys()) if all_data else []

if all_data:
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_data)
    logging.info(f"\n✅ CSV file created: {csv_file} with {len(all_data)} entries")
else:
    logging.error("\n❌ No data found to write to CSV")


# -----------------------------------------
# 4. Upload CSV to Oracle DB using oracledb
# -----------------------------------------
if all_data:
    # Handle credentials
    if use_test_creds:
        db_user = config["test_credentials"]["user"]
        db_pass = config["test_credentials"]["password"]
        db_dsn = config["test_credentials"]["dsn"]
    else:
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        db_user = config["db_credentials"]["user"]
        db_pass = get_secret_value(config["db_credentials"]["pass_secret_ocid"], signer=signer)
        db_dsn = config["db_credentials"]["dsn"]

    os.environ['TNS_ADMIN'] = wallet_path
    conn = oracledb.connect(
        user=db_user,
        password=db_pass,
        dsn=db_dsn
    )
    cursor = conn.cursor()

    # Column definitions (for placeholder generation)
    column_defs = ",\n".join([
        "id VARCHAR2(1000)",
        "compartment_id VARCHAR2(1000)",
        "current_custom_action_timeout_in_mins NUMBER",
        "current_patching_component VARCHAR2(1000)",
        "custom_action_timeout_in_mins NUMBER",
        "database_software_image_id VARCHAR2(1000)",
        "description VARCHAR2(10000)",
        "display_name VARCHAR2(500)",
        "estimated_db_server_patching_time NUMBER",
        "estimated_network_switches_patching_time NUMBER",
        "estimated_storage_server_patching_time NUMBER",
        "total_estimated_patching_time NUMBER",
        "is_custom_action_timeout_enabled VARCHAR2(10)",
        "is_dst_file_update_enabled VARCHAR2(10)",
        "is_maintenance_run_granular VARCHAR2(10)",
        "lifecycle_details VARCHAR2(10000)",
        "lifecycle_state VARCHAR2(50)",
        "maintenance_subtype VARCHAR2(1000)",
        "maintenance_type VARCHAR2(1000)",
        "patch_failure_count NUMBER",
        "patch_id VARCHAR2(50)",
        "patching_end_time TIMESTAMP",
        "patching_mode VARCHAR2(50)",
        "patching_start_time TIMESTAMP",
        "patching_status VARCHAR2(50)",
        "peer_maintenance_run_id VARCHAR2(1000)",
        "peer_maintenance_run_ids CLOB",
        "target_db_server_version VARCHAR2(1000)",
        "target_resource_id VARCHAR2(200)",
        "target_resource_type VARCHAR2(1000)",
        "target_storage_server_version VARCHAR2(1000)",
        "time_ended TIMESTAMP",
        "time_scheduled TIMESTAMP",
        "time_started TIMESTAMP",
        "total_time_taken_in_mins NUMBER"
    ])

    try:
        cursor.execute(f"TRUNCATE TABLE {exa_maintenance_metrics_table}")
        logging.info(f"✅ Truncated table {exa_maintenance_metrics_table}")
    except Exception as e:
        logging.error(f"❌ Failed to truncate table {exa_maintenance_metrics_table}: {e}")
        raise

    # Prepare rows and insert
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        rows = [tuple(row[col] for col in reader.fieldnames) for row in reader]

    columns = [desc.split()[0] for desc in column_defs.split(",\n")]
    placeholders = ",".join([f":{i+1}" for i in range(len(columns))])
    insert_sql = f"INSERT INTO {exa_maintenance_metrics_table} ({','.join(columns)}) VALUES ({placeholders})"
    cursor.executemany(insert_sql, rows)
    conn.commit()

    logging.info(f"\n📥 Uploaded {len(rows)} rows to table {exa_maintenance_metrics_table}.")
