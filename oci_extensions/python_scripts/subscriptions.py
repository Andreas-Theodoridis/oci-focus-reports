import oci
import os
import csv
import json
import logging
import base64
import fnmatch
import shutil
import gzip
from datetime import datetime, timedelta
import oracledb

app_dir    = "/home/opc/oci_extensions"
config_dir = os.path.join(app_dir, "config")
log_dir    = os.path.join(app_dir, "logs")
output_dir = os.path.join(app_dir, "data", "subscriptions")

os.makedirs(log_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

def load_config(name):
    with open(os.path.join(config_dir, name)) as f:
        return json.load(f)

config   = load_config("metrics_config.json")
dbconfig = load_config("db_config.json")

log_file_pattern = config["oci_subscriptions_file_name_pattern"]
oci_subscriptions_table = dbconfig["oci_subscriptions_table"]
db_user = dbconfig["db_user"]
db_pass = dbconfig["db_password"]
db_dsn = dbconfig["db_dsn"]
wallet_path = dbconfig["wallet_dir"]
use_test_creds = dbconfig.get("use_test_credentials", False)

# Oracle Thick Client
oracledb.init_oracle_client(lib_dir=dbconfig["oracle_client_lib_dir"])

# Logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(log_dir, f"oci_subscriptions_{timestamp}.log")
latest_log_symlink = os.path.join(log_dir, "latest_subscriptions.log")

for filename in os.listdir(log_dir):
    if fnmatch.fnmatch(filename, log_file_pattern) and filename != os.path.basename(log_filename):
        full_path = os.path.join(log_dir, filename)
        gz_path = full_path + '.gz'
        with open(full_path, 'rb') as f_in, gzip.open(gz_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.remove(full_path)

cutoff_date = datetime.now() - timedelta(days=30)
for filename in os.listdir(log_dir):
    if filename.endswith(".gz"):
        full_path = os.path.join(log_dir, filename)
        mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
        if mtime < cutoff_date:
            os.remove(full_path)

if os.path.exists(latest_log_symlink) or os.path.islink(latest_log_symlink):
    os.remove(latest_log_symlink)
os.symlink(f"oci_subscriptions_{timestamp}.log", latest_log_symlink)

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

signer     = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
tenancy_id = signer.tenancy_id

def get_secret_value(secret_ocid, signer):
    secrets_client = oci.secrets.SecretsClient({}, signer=signer)
    bundle = secrets_client.get_secret_bundle(secret_id=secret_ocid)
    base64_secret = bundle.data.secret_bundle_content.content
    return base64.b64decode(base64_secret).decode("utf-8")

def get_all_subscription_ids():
    client = oci.onesubscription.OrganizationSubscriptionClient(config={}, signer=signer)
    response = client.list_organization_subscriptions(compartment_id=tenancy_id)
    return [sub.id for sub in response.data]

def list_all_subscriptions(subscription_ids):
    csv_path = os.path.join(output_dir, f"oci_subscriptions_combined.csv")

    fieldnames = [
        "subscription_id", "iso_code", "name", "std_precision",
        "service_name", "status", "available_amount", "booking_opty_number",
        "commitment_services", "csi", "data_center_region", "funded_allocation_value",
        "id", "is_intent_to_pay", "net_unit_price", "operation_type", "order_number",
        "original_promo_amount", "partner_transaction_type", "pricing_model",
        "product_name", "product_part_number", "product_provisioning_group",
        "product_unit_of_measure", "program_type", "promo_type", "quantity", "substatus",
        "time_end", "time_start", "total_value", "used_amount"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        client = oci.onesubscription.SubscriptionClient(config={}, signer=signer)

        for subscription_id in subscription_ids:
            try:
                logging.info(f"📦 Fetching data for subscription: {subscription_id}")
                resp = client.list_subscriptions(compartment_id=tenancy_id, subscription_id=subscription_id)
                subs = resp.data

                for sub in subs:
                    for svc in sub._subscribed_services or [None]:
                        row = {
                            "subscription_id": subscription_id,
                            "iso_code": sub._currency.iso_code if sub._currency else "",
                            "name": sub._currency.name if sub._currency else "",
                            "std_precision": sub._currency.std_precision if sub._currency else "",
                            "service_name": sub._service_name or "",
                            "status": sub._status or "",
                            "available_amount": svc.available_amount if svc else "",
                            "booking_opty_number": svc.booking_opty_number if svc else "",
                            "commitment_services": svc.commitment_services if svc else "",
                            "csi": svc.csi if svc else "",
                            "data_center_region": svc.data_center_region if svc else "",
                            "funded_allocation_value": svc.funded_allocation_value if svc else "",
                            "id": sub.id if hasattr(sub, 'id') else "",
                            "is_intent_to_pay": svc.is_intent_to_pay if svc else "",
                            "net_unit_price": svc.net_unit_price if svc else "",
                            "operation_type": svc.operation_type if svc else "",
                            "order_number": svc.order_number if svc else "",
                            "original_promo_amount": svc.original_promo_amount if svc else "",
                            "partner_transaction_type": svc.partner_transaction_type if svc else "",
                            "pricing_model": svc.pricing_model if svc else "",
                            "product_name": svc.product.name if svc and svc.product else "",
                            "product_part_number": svc.product.part_number if svc and svc.product else "",
                            "product_provisioning_group": svc.product.provisioning_group if svc and svc.product else "",
                            "product_unit_of_measure": svc.product.unit_of_measure if svc and svc.product else "",
                            "program_type": svc.program_type if svc else "",
                            "promo_type": svc.promo_type if svc else "",
                            "quantity": svc.quantity if svc else "",
                            "substatus": svc.status if svc else "",
                            "time_end": svc.time_end.isoformat() if svc and svc.time_end else "",
                            "time_start": svc.time_start.isoformat() if svc and svc.time_start else "",
                            "total_value": svc.total_value if svc else "",
                            "used_amount": svc.used_amount if svc else "",
                        }
                        writer.writerow(row)

            except Exception as e:
                logging.error(f"❌ Failed to fetch subscription {subscription_id}: {e}")

    logging.info(f"✅ All subscription data written to: {csv_path}")
    return csv_path

def upload_csv_to_oracle(csv_path, table_name=oci_subscriptions_table):
    os.environ['TNS_ADMIN'] = wallet_path
    try:
        conn = oracledb.connect(
            user=db_user,
            password=get_secret_value(dbconfig["db_credentials"]["pass_secret_ocid"], signer),
            dsn=db_dsn
        )
        cursor = conn.cursor()
        cursor.execute(f"TRUNCATE TABLE {table_name}")
        logging.info(f"Cleared existing data from {table_name}")

        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames
            placeholders = ", ".join([f":{i+1}" for i in range(len(columns))])
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

            rows = [tuple(row[col] for col in columns) for row in reader]
            cursor.executemany(insert_sql, rows)
            conn.commit()
            logging.info(f"✅ Inserted {cursor.rowcount} rows into {table_name}")

    except Exception as e:
        logging.error(f"❌ Error uploading CSV to Oracle DB: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# MAIN
if __name__ == "__main__":
    sub_ids = get_all_subscription_ids()
    logging.info(f"Found {len(sub_ids)} subscriptions.")
    csv_file = list_all_subscriptions(sub_ids)
    if csv_file:
        upload_csv_to_oracle(csv_file)

