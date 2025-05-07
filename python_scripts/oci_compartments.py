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
output_dir = os.path.join(app_dir, "data", "compartments")

os.makedirs(log_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Load config
def load_config(name):
    with open(os.path.join(config_dir, name)) as f:
        return json.load(f)

config   = load_config("metrics_config.json")
dbconfig = load_config("db_config.json")

compartment_ocid = config["gsis_comp_ocid"]
log_file_pattern= config["gsis_compartments_file_name_pattern"]

compartments_table = dbconfig["compartments_table"]
db_user = dbconfig["db_user"]
db_pass = dbconfig["db_password"]
db_dsn = dbconfig["db_dsn"]
wallet_path = dbconfig["wallet_dir"]
use_test_creds = dbconfig.get("use_test_credentials", False)

# 💡 Initialize Oracle Thick Client
oracledb.init_oracle_client(lib_dir=dbconfig["oracle_client_lib_dir"])

# Create timestamped log filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(log_dir, f"gsis_compartments_{timestamp}.log")
latest_log_symlink = os.path.join(log_dir, "latest_gsis_compartments.log")
# Zip all previous .log files (except current one)
for filename in os.listdir(log_dir):
    if fnmatch.fnmatch(filename, log_file_pattern) and filename != os.path.basename(log_filename):
        full_path = os.path.join(log_dir, filename)
        gz_path = full_path + '.gz'
        with open(full_path, 'rb') as f_in, gzip.open(gz_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.remove(full_path)

# Delete .gz logs older than 30 days
cutoff_date = datetime.now() - timedelta(days=30)
for filename in os.listdir(log_dir):
    if filename.endswith(".gz"):
        full_path = os.path.join(log_dir, filename)
        mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
        if mtime < cutoff_date:
            os.remove(full_path)

# Update 'latest.log' symlink
if os.path.exists(latest_log_symlink) or os.path.islink(latest_log_symlink):
    os.remove(latest_log_symlink)
os.symlink(f"gsis_compartments_{timestamp}.log", latest_log_symlink)

# Setup logging
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def get_secret_value(secret_ocid, signer):
    secrets_client = oci.secrets.SecretsClient({}, signer=signer)
    bundle = secrets_client.get_secret_bundle(secret_id=secret_ocid)
    base64_secret = bundle.data.secret_bundle_content.content
    return base64.b64decode(base64_secret).decode("utf-8")

def build_compartment_hierarchy(compartments):
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

    return list(hierarchy.values())  # Convert back to list

def get_all_compartments():
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
    identity_client = oci.identity.IdentityClient({}, signer=signer)

    tenancy_ocid = compartment_ocid
    compartments = []

    response = identity_client.list_compartments(tenancy_ocid, compartment_id_in_subtree=True, access_level="ACCESSIBLE")

    for compartment in response.data:
        compartments.append({
            "Compartment ID": compartment.id,
            "Name": compartment.name,
            "Description": compartment.description,
            "Lifecycle State": compartment.lifecycle_state,
            "Time Created": str(compartment.time_created),
            "Parent ID": compartment.compartment_id,
            "Parent": compartments[-1]["Name"] if compartments else None  # Assign the previous compartment's name as parent
        })

    hierarchy = build_compartment_hierarchy(compartments)
    return hierarchy  # Return as a list of dictionaries

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
    output.seek(0)
    return output.getvalue()

def write_csv_locally(csv_data, file_path):
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

    table_name = compartments_table
    merge_sql = f"""
    MERGE INTO {table_name} tgt
    USING (
        SELECT :1 AS "Compartment ID", :2 AS "Name", :3 AS "Description",
               :4 AS "Lifecycle State", :5 AS "Time Created", :6 AS "Parent ID",
               :7 AS "Parent", :8 AS "Path"
        FROM dual
    ) src
    ON (tgt."Compartment_ID" = src."Compartment ID")
    WHEN MATCHED THEN UPDATE SET
        tgt."Name" = src."Name",
        tgt."Description" = src."Description",
        tgt."Lifecycle_State" = src."Lifecycle State",
        tgt."Time_Created" = src."Time Created",
        tgt."Parent_ID" = src."Parent ID",
        tgt.PARENT = src."Parent",
        tgt."Path" = src."Path"
    WHEN NOT MATCHED THEN INSERT (
        "Compartment_ID", "Name", "Description", "Lifecycle_State", "Time_Created",
        "Parent_ID", PARENT, "Path"
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
        output_path = os.path.join(output_dir, "compartments_gsis_data.csv")
        #file_path = "compartments_data.csv"
        write_csv_locally(csv_data, output_path)

        # Upload to Oracle DB
        if use_test_creds:
            db_user = dbconfig["test_credentials"]["user"]
            db_pass = dbconfig["test_credentials"]["password"]
            db_dsn = dbconfig["test_credentials"]["dsn"]
        else:
            db_user = dbconfig["db_credentials"]["user"]
            db_pass = get_secret_value(dbconfig["db_credentials"]["pass_secret_ocid"], signer=oci.auth.signers.InstancePrincipalsSecurityTokenSigner())
            db_dsn = dbconfig["db_credentials"]["dsn"]

        upload_csv_to_oracle(csv_data, db_user, db_pass, db_dsn)

        logging.info("Data processed and uploaded successfully.")
    except Exception as e:
        logging.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
