import json
import oci
import csv
import os
import logging
import base64
import gzip
import shutil
from datetime import datetime, timedelta
import fnmatch
import oracledb
from oci.generative_ai.generative_ai_client import GenerativeAiClient

# === Set Directories ===
app_dir = "/home/opc/oci-focus-reports"
config_dir = os.path.join(app_dir, "config")
log_dir = os.path.join(app_dir, "logs")
OLD_LOG_DIR = os.path.join(log_dir, "old")
output_dir = os.path.join(app_dir, "data", "aimodels")

os.makedirs(log_dir, exist_ok=True)
os.makedirs(OLD_LOG_DIR, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# === Load Config Files ===
def load_config(name):
    with open(os.path.join(config_dir, name)) as f:
        return json.load(f)

config = load_config("config.json")

compartment_ocid = config["comp_ocid"]
aimodel_table = config["aimodel_table"]
db_user = config["db_user"]
db_pass = config["db_password"]
db_dsn = config["db_dsn"]
wallet_path = config["wallet_dir"]

# 💡 Initialize Oracle Thick Client
oracledb.init_oracle_client(lib_dir=config["oracle_client_lib_dir"])

# === Logging Setup ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(log_dir, f"genai_{timestamp}.log")
latest_log_symlink = os.path.join(log_dir, "latest_genai.log")
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

# Update symlink
if os.path.exists(latest_log_symlink) or os.path.islink(latest_log_symlink):
    os.remove(latest_log_symlink)
os.symlink(os.path.basename(log_filename), latest_log_symlink)

# === Secret Retrieval ===
def get_secret_value(secret_ocid, signer):
    secrets_client = oci.secrets.SecretsClient({}, signer=signer)
    bundle = secrets_client.get_secret_bundle(secret_id=secret_ocid)
    return base64.b64decode(bundle.data.secret_bundle_content.content).decode("utf-8")

# === Upload CSV to Oracle DB ===
def upload_csv_to_oracle(csv_path, table_name, signer):
    logging.info(f"🔼 Uploading CSV to Oracle DB: {csv_path}")
    os.environ["TNS_ADMIN"] = wallet_path

    conn = None
    cursor = None

    try:
        db_password = db_pass
        if "pass_secret_ocid" in config.get("db_credentials", {}):
            db_password = get_secret_value(config["db_credentials"]["pass_secret_ocid"], signer)

        conn = oracledb.connect(
            user=db_user,
            password=db_password,
            dsn=db_dsn
        )
        cursor = conn.cursor()

        # Truncate existing data
        cursor.execute(f"TRUNCATE TABLE {table_name}")
        logging.info(f"🧹 Truncated table {table_name}")

        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')

            columns = [
                "MODEL_ID", "MODEL_NAME", "API_FORMAT", "IS_DEFAULT", "REGION",
                "TEMPERATURE", "TOP_P", "TOP_K", "FREQUENCY_PENALTY", "PRESENCE_PENALTY"
            ]

            placeholders = ", ".join([f":{i+1}" for i in range(len(columns))])
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

            rows = [tuple(row[col] for col in columns) for row in reader]
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

# === Collect GenAI Chat Models and Store ===
def collect_generative_ai_models():
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
    regions_to_query = ["eu-frankfurt-1", "us-chicago-1"]

    all_models = []

    for region in regions_to_query:
        try:
            logging.info(f"📡 Querying Generative AI models in region: {region}")
            genai_client = GenerativeAiClient(config={"region": region}, signer=signer)
            response = genai_client.list_models(compartment_id=compartment_ocid)

            for model in response.data.items:
                if set(model.capabilities or []) != {"CHAT"}:
                    continue  # Skip non-chat models

                vendor = (model.vendor or "").lower()
                api_format = "COHERE" if vendor == "cohere" else "GENERIC"

                all_models.append({
                    "MODEL_ID": model.id,
                    "MODEL_NAME": model.display_name,
                    "API_FORMAT": api_format,
                    "IS_DEFAULT": "N",
                    "REGION": region,
                    "TEMPERATURE": None,
                    "TOP_P": None,
                    "TOP_K": None,
                    "FREQUENCY_PENALTY": None,
                    "PRESENCE_PENALTY": None
                })

            logging.info(f"✅ Retrieved {len(all_models)} chat models from {region}")

        except Exception as e:
            logging.warning(f"⚠️ Failed to retrieve models from {region}: {e}")

    if all_models:
        csv_file = os.path.join(output_dir, "genai_models.csv")
        columns = [
            "MODEL_ID", "MODEL_NAME", "API_FORMAT", "IS_DEFAULT", "REGION",
            "TEMPERATURE", "TOP_P", "TOP_K", "FREQUENCY_PENALTY", "PRESENCE_PENALTY"
        ]

        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns, delimiter=';')
            writer.writeheader()
            writer.writerows(all_models)

        logging.info(f"📝 GenAI chat model CSV written to {csv_file}")
        upload_csv_to_oracle(csv_file, aimodel_table, signer)
    else:
        logging.warning("⚠️ No CHAT models found in the selected regions.")

# === Entry Point ===
if __name__ == "__main__":
    collect_generative_ai_models()