import json
import oci
import csv
import io
import oracledb
from datetime import datetime, timedelta
import base64
import os
import fnmatch
import shutil
import gzip
import logging

app_dir    = "/home/opc/oci-focus-reports"
config_dir = os.path.join(app_dir, "config")
log_dir    = os.path.join(app_dir, "logs")
OLD_LOG_DIR = os.path.join(log_dir, "old")
output_dir = os.path.join(app_dir, "data", "compartments")

os.makedirs(log_dir, exist_ok=True)
os.makedirs(OLD_LOG_DIR, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Load config
def load_config(name):
    with open(os.path.join(config_dir, name)) as f:
        return json.load(f)

config   = load_config("config.json")

compartment_ocid = config["comp_ocid"]
log_file_pattern= config["compartments_file_name_pattern"]

compartments_table = config["compartments_table"]
db_user = config["db_user"]
db_pass = config["db_password"]
db_dsn = config["db_dsn"]
wallet_path = config["wallet_dir"]
use_test_creds = config.get("use_test_credentials", False)

# 💡 Initialize Oracle Thick Client
oracledb.init_oracle_client(lib_dir=config["oracle_client_lib_dir"])

# Create timestamped log filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(log_dir, f"compartments_{timestamp}.log")
latest_log_symlink = os.path.join(log_dir, "latest_compartments.log")
# Setup logging
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
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
os.symlink(f"compartments_{timestamp}.log", latest_log_symlink)

def get_secret_value(secret_ocid, signer):
    secrets_client = oci.secrets.SecretsClient({}, signer=signer)
    bundle = secrets_client.get_secret_bundle(secret_id=secret_ocid)
    base64_secret = bundle.data.secret_bundle_content.content
    logging.info("✅ Secret retrieved.")
    return base64.b64decode(base64_secret).decode("utf-8")

def build_compartment_hierarchy(compartments):
    logging.info("🧭 Building compartment hierarchy...")
    """Builds a hierarchy from the compartment list, supporting multiple levels"""
    hierarchy = {}

    # First, organize compartments by their ID
    compartments_by_id = {comp['Compartment ID']: comp for comp in compartments}

    # Add a special root entry for the tenancy
    hierarchy[compartment_ocid] = {
        "Compartment ID": compartment_ocid, "Name": "Root", "Parent": None, "Parent ID": None, "Path": ""
    }

    # Recursively build paths for all compartments
    def get_path(comp_id):
        if comp_id in hierarchy:
            return hierarchy[comp_id]["Path"]
        parent_id = compartments_by_id.get(comp_id, {}).get("Parent ID", compartment_ocid)
        parent_path = get_path(parent_id) if parent_id else ""
        if parent_path:
            return f"{parent_path}/{compartments_by_id[comp_id]['Name']}"
        else:
            return compartments_by_id[comp_id]["Name"]

    # Assign paths to all compartments
    for comp in compartments:
        comp["Path"] = get_path(comp["Compartment ID"])
        hierarchy[comp["Compartment ID"]] = comp

    logging.info("✅ Compartment hierarchy built.")
    return list(hierarchy.values())  # Convert back to list

def get_all_compartments():
    logging.info("🌐 Fetching all compartments from OCI (with pagination)...")
    
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
    identity_client = oci.identity.IdentityClient({}, signer=signer)

    tenancy_ocid = compartment_ocid
    compartments = []

    # This handles pagination automatically
    list_response = oci.pagination.list_call_get_all_results(
        identity_client.list_compartments,
        compartment_id=tenancy_ocid,
        compartment_id_in_subtree=True,
        access_level="ACCESSIBLE"
    )

    for compartment in list_response.data:
        compartments.append({
            "Compartment ID": compartment.id,
            "Name": compartment.name,
            "Description": compartment.description,
            "Lifecycle State": compartment.lifecycle_state,
            "Time Created": str(compartment.time_created),
            "Parent ID": compartment.compartment_id,
            "Parent": None  # You'll build proper hierarchy later
        })

    logging.info(f"✅ Retrieved {len(compartments)} compartments (all pages).")

    hierarchy = build_compartment_hierarchy(compartments)
    return hierarchy

def convert_json_to_csv(data):
    """Convert a list of JSON objects to CSV format"""
    output = io.StringIO()

    # Add "Parent" to fieldnames list
    fieldnames = [
        "Compartment ID", "Name", "Description", "Lifecycle State", "Time Created",
        "Parent ID", "Parent", "Path"
    ]

    csv_writer = csv.DictWriter(output, fieldnames=fieldnames)
    csv_writer.writeheader()
    csv_writer.writerows(data)
    logging.info("✅ Conversion to CSV complete.")
    output.seek(0)
    return output.getvalue()

def write_csv_locally(csv_data, file_path):
    logging.info(f"💾 Writing CSV locally to {file_path}...")
    """Write CSV data to a local file"""
    with open(file_path, 'w', newline='') as csv_file:
        csv_file.write(csv_data)
    logging.info(f"✅ CSV data written to {file_path}")

def upload_csv_to_oracle(csv_data, db_user, db_pass, db_dsn):
    """Uploads CSV data to an Oracle Database table"""
    # Parse the CSV data into rows
    csv_rows = []
    csv_reader = csv.DictReader(io.StringIO(csv_data))
    for row in csv_reader:
        csv_rows.append({
            "Compartment ID": row["Compartment ID"],
            "Name": row["Name"],
            "Description": row["Description"],
            "Lifecycle State": row["Lifecycle State"],
            "Time Created": row["Time Created"],
            "Parent ID": row["Parent ID"],
            "Parent": row["Parent"],
            "Path": row["Path"]
        })

    if not csv_rows:
        logging.warning("⚠️ No data to upload.")
        return
    
    os.environ['TNS_ADMIN'] = wallet_path
    conn = oracledb.connect(
        user=db_user,
        password=db_pass,
        dsn=db_dsn,
        config_dir=wallet_path,
        wallet_location=wallet_path,
        wallet_password=db_pass
    )
    cursor = conn.cursor()

    # Prevent ORA-12838 error
    cursor.execute("ALTER SESSION DISABLE PARALLEL DML")

    table_name = compartments_table
    merge_sql = f"""
    MERGE INTO {table_name} tgt
    USING (
        SELECT :1 AS "Compartment ID", :2 AS "Name", :3 AS "Description",
               :4 AS "Lifecycle State", :5 AS "Time Created", :6 AS "Parent ID",
               :7 AS "Parent", :8 AS "Path"
        FROM dual
    ) src
    ON (tgt."COMPARTMENT_ID" = src."Compartment ID")
    WHEN MATCHED THEN UPDATE SET
        tgt."NAME" = src."Name",
        tgt."DESCRIPTION" = src."Description",
        tgt."LIFECYCLE_STATE" = src."Lifecycle State",
        tgt."TIME_CREATED" = src."Time Created",
        tgt."PARENT_ID" = src."Parent ID",
        tgt.PARENT = src."Parent",
        tgt."PATH" = src."Path"
    WHEN NOT MATCHED THEN INSERT (
        "COMPARTMENT_ID", "NAME", "DESCRIPTION", "LIFECYCLE_STATE", "TIME_CREATED",
        "PARENT_ID", PARENT, "PATH"
    )
    VALUES (
        src."Compartment ID", src."Name", src."Description", src."Lifecycle State",
        src."Time Created", src."Parent ID", src."Parent", src."Path"
    )
    """

    logging.info(f"⬆️ Uploading {len(csv_rows)} rows to {table_name}...")
    data = [
        (
            row["Compartment ID"],
            row["Name"],
            row["Description"],
            row["Lifecycle State"],
            row["Time Created"],
            row["Parent ID"],
            row["Parent"],
            row["Path"]
        ) for row in csv_rows
    ]

    cursor.executemany(merge_sql, data)
    conn.commit()
    cursor.close()
    conn.close()
    logging.info("✅ Upload complete.")

def main():
    """Main function to retrieve compartments, convert to CSV, write locally, and upload to Oracle DB"""
    try:
        # Fetch compartment data
        compartment_data = get_all_compartments()  # This returns a list of dictionaries

        # Convert data to CSV format
        csv_data = convert_json_to_csv(compartment_data)

        # Write the CSV data locally to a file
        output_path = os.path.join(output_dir, "compartments_data.csv")
        #file_path = "compartments_data.csv"
        write_csv_locally(csv_data, output_path)

        # Upload to Oracle DB
        if use_test_creds:
            db_user = config["test_credentials"]["user"]
            db_pass = config["test_credentials"]["password"]
            db_dsn = config["test_credentials"]["dsn"]
        else:
            db_user = config["db_credentials"]["user"]
            db_pass = get_secret_value(config["db_credentials"]["pass_secret_ocid"], signer=oci.auth.signers.InstancePrincipalsSecurityTokenSigner())
            db_dsn = config["db_credentials"]["dsn"]

        upload_csv_to_oracle(csv_data, db_user, db_pass, db_dsn)

        logging.info("Data processed and uploaded successfully.")
    except Exception as e:
        logging.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
