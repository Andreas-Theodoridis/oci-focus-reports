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

# === Set Directories ===
app_dir    = "/home/opc/oci-focus-reports"
config_dir = os.path.join(app_dir, "config")
log_dir    = os.path.join(app_dir, "logs")
output_dir = os.path.join(app_dir, "data", "resources")

os.makedirs(log_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# === Load Config Files ===
def load_config(name):
    with open(os.path.join(config_dir, name)) as f:
        return json.load(f)

config   = load_config("config.json")

compartment_ocid = config["comp_ocid"]
log_file_pattern = config["resources_file_name_pattern"]

resources_table = config["resources_table"]
db_user = config["db_user"]
db_pass = config["db_password"]
db_dsn = config["db_dsn"]
wallet_path = config["wallet_dir"]
use_test_creds = config.get("use_test_credentials", False)

# 💡 Initialize Oracle Thick Client
oracledb.init_oracle_client(lib_dir=config["oracle_client_lib_dir"])

# === Logging Setup ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(log_dir, f"resources_{timestamp}.log")
latest_log_symlink = os.path.join(log_dir, "latest_resources.log")

# Zip older log files
for filename in os.listdir(log_dir):
    if fnmatch.fnmatch(filename, log_file_pattern) and filename != os.path.basename(log_filename):
        full_path = os.path.join(log_dir, filename)
        with open(full_path, 'rb') as f_in, gzip.open(full_path + ".gz", 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.remove(full_path)

# Cleanup .gz logs older than 30 days
cutoff = datetime.now() - timedelta(days=30)
for filename in os.listdir(log_dir):
    if filename.endswith(".gz"):
        path = os.path.join(log_dir, filename)
        if datetime.fromtimestamp(os.path.getmtime(path)) < cutoff:
            os.remove(path)

# Update symlink
if os.path.exists(latest_log_symlink) or os.path.islink(latest_log_symlink):
    os.remove(latest_log_symlink)
os.symlink(os.path.basename(log_filename), latest_log_symlink)

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# === Search Resources Across All Regions ===
def search_all_regions_and_save():
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
    identity_client = oci.identity.IdentityClient({}, signer=signer)
    tenancy_id = signer.tenancy_id

    try:
        regions_response = identity_client.list_region_subscriptions(tenancy_id)
        regions = [r.region_name for r in regions_response.data]
        logging.info(f"🔁 Found {len(regions)} regions: {regions}")

        all_results = []

        for region in regions:
            logging.info(f"🌍 Switching to region: {region}")
            config = {"region": region}
            search_client = oci.resource_search.ResourceSearchClient(config=config, signer=signer)

            search_details = oci.resource_search.models.StructuredSearchDetails(
                type="Structured",
                query="query all resources"
            )

            try:
                response = search_client.search_resources(search_details)
                items = response.data.items

                while response.has_next_page:
                    response = search_client.search_resources(search_details, page=response.next_page)
                    items.extend(response.data.items)

                for item in items:
                    defined_tags = json.dumps(item.defined_tags or {})
                    freeform_tags = json.dumps(item.freeform_tags or {})
                    system_tags = json.dumps(item.system_tags or {})
                    additional_details = json.dumps(item.additional_details or {})

                    all_results.append({
                        "display-name": item.display_name,
                        "identifier": item.identifier,
                        "region": region,
                        "resource-type": item.resource_type,
                        "defined-tags": defined_tags,
                        "freeform-tags": freeform_tags,
                        "system-tags": system_tags,
                        "compartment-id": item.compartment_id,
                        "availability-domain": getattr(item, "availability_domain", "N/A"),
                        "time-created": item.time_created.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] if item.time_created else None,
                        "additional-details": additional_details
                    })

                logging.info(f"✅ {len(items)} items retrieved from {region}")

            except oci.exceptions.ServiceError as e:
                logging.warning(f"⚠️ Could not search in {region}: {e}")

        # === Save to JSON
        json_file = os.path.join(output_dir, f"resources.json")
        with open(json_file, "w", encoding='utf-8') as f:
            json.dump(all_results, f, indent=4)
        logging.info(f"📝 JSON written to {json_file}")

        # === Save to CSV
        csv_file = os.path.join(output_dir, f"resources.csv")
        if all_results:
            fieldnames = all_results[0].keys()
            with open(csv_file, "w", newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
                writer.writeheader()
                writer.writerows(all_results)
            logging.info(f"📁 CSV written to {csv_file}")
            #print(f"CSV saved to {csv_file}")

            # === Upload to Oracle DB
            upload_csv_to_oracle(csv_file, resources_table, signer)

        else:
            logging.warning("⚠️ No data collected from any region.")

    except Exception as e:
        logging.error(f"❌ Failed during multi-region search: {e}")

# Upload to DB
def get_secret_value(secret_ocid, signer):
    secrets_client = oci.secrets.SecretsClient({}, signer=signer)
    bundle = secrets_client.get_secret_bundle(secret_id=secret_ocid)
    return base64.b64decode(bundle.data.secret_bundle_content.content).decode("utf-8")


def upload_csv_to_oracle(csv_path, table_name, signer):
    logging.info(f"🔼 Uploading CSV to Oracle DB: {csv_path}")
    os.environ["TNS_ADMIN"] = wallet_path

    conn = None
    cursor = None

    try:
        db_password = db_pass
        if "pass_secret_ocid" in config.get("db_credentials", {}):
            db_password = get_secret_value(config["db_credentials"]["pass_secret_ocid"], signer)

        conn = oracledb.connect(user=db_user, password=db_password, dsn=db_dsn)
        cursor = conn.cursor()

        cursor.execute(f"TRUNCATE TABLE {table_name}")
        logging.info(f"🧹 Truncated table {table_name}")

        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')

            column_mapping = {
                "display-name": "DISPLAY_NAME",
                "identifier": "IDENTIFIER",
                "region": "REGION",
                "resource-type": "RESOURCE_TYPE",
                "defined-tags": "DEFINED_TAGS",
                "freeform-tags": "FREEFORM_TAGS",
                "system-tags": "SYSTEM_TAGS",
                "compartment-id": "COMPARTMENT_ID",
                "availability-domain": "AVAILABILITY_DOMAIN",
                "time-created": "TIME_CREATED",
                "additional-details": "ADDITIONAL_DETAILS"
            }

            columns = list(column_mapping.values())

            # Build correct placeholders with TO_TIMESTAMP for TIME_CREATED
            placeholders = []
            for idx, col in enumerate(columns):
                bind_var = f":{idx + 1}"
                if col == "TIME_CREATED":
                    placeholders.append(f"TO_TIMESTAMP({bind_var}, 'YYYY-MM-DD HH24:MI:SS.FF3')")
                else:
                    placeholders.append(bind_var)

            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"

            # Prepare rows
            rows = []
            for row in reader:
                values = []
                for key in column_mapping.keys():
                    val = row.get(key)
                    if key == "time-created":
                        if val.strip() == "":
                            values.append(None)
                        else:
                            values.append(val.strip())  # already in correct format
                    else:
                        values.append(val)
                rows.append(tuple(values))

            cursor.executemany(insert_sql, rows)
            conn.commit()
            logging.info(f"✅ Inserted {cursor.rowcount} rows into {table_name}")

    except Exception as e:
        logging.error(f"❌ DB upload failed: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    search_all_regions_and_save()