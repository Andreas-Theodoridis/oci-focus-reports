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

# ---- Paths ------------------------------------------------------------------
app_dir    = "/home/opc/oci-focus-reports"
config_dir = os.path.join(app_dir, "config")
log_dir    = os.path.join(app_dir, "logs")
OLD_LOG_DIR = os.path.join(log_dir, "old")
output_dir = os.path.join(app_dir, "data", "subscriptions")

os.makedirs(log_dir, exist_ok=True)
os.makedirs(OLD_LOG_DIR, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# ---- Config -----------------------------------------------------------------
def load_config(name):
    with open(os.path.join(config_dir, name)) as f:
        return json.load(f)

config   = load_config("config.json")

log_file_pattern                 = config["oci_subscriptions_file_name_pattern"]
oci_subscriptions_table          = config["oci_subscriptions_table"]
oci_commitments_table            = config["oci_subscription_commitments_table"]
db_user                          = config["db_user"]
db_pass                          = config["db_password"]
db_dsn                           = config["db_dsn"]
wallet_path                      = config["wallet_dir"]
use_test_creds                   = config.get("use_test_credentials", False)

# Oracle Thick Client
oracledb.init_oracle_client(lib_dir=config["oracle_client_lib_dir"])

# ---- Logging ---------------------------------------------------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(log_dir, f"oci_subscriptions_{timestamp}.log")
latest_log_symlink = os.path.join(log_dir, "latest_subscriptions.log")
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# Zip old logs
for filename in os.listdir(log_dir):
    if (
        fnmatch.fnmatch(filename, log_file_pattern)
        and filename != os.path.basename(log_filename)
        and not filename.endswith(".gz")
    ):
        full_path = os.path.join(log_dir, filename)
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

if os.path.exists(latest_log_symlink) or os.path.islink(latest_log_symlink):
    os.remove(latest_log_symlink)
os.symlink(f"oci_subscriptions_{timestamp}.log", latest_log_symlink)

# ---- Auth / Tenancy ---------------------------------------------------------
signer     = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
tenancy_id = signer.tenancy_id

# ---- Helpers ----------------------------------------------------------------
def get_secret_value(secret_ocid, signer):
    secrets_client = oci.secrets.SecretsClient({}, signer=signer)
    bundle = secrets_client.get_secret_bundle(secret_id=secret_ocid)
    base64_secret = bundle.data.secret_bundle_content.content
    return base64.b64decode(base64_secret).decode("utf-8")

def log_and_execute(cursor, sql):
    logging.info(f"➡️ Executing SQL:\n{sql}")
    cursor.execute(sql)

# ---- Data Pull --------------------------------------------------------------
def get_all_subscription_ids():
    client = oci.onesubscription.OrganizationSubscriptionClient(config={}, signer=signer)
    response = client.list_organization_subscriptions(compartment_id=tenancy_id)
    return [sub.id for sub in response.data]

def list_all_subscriptions(subscription_ids):
    """
    Writes two CSVs:
      1) oci_subscriptions_combined.csv         -> same columns as before (no schema change)
      2) oci_subscription_commitments.csv       -> NEW child rows, one per commitment
    """
    subs_csv_path = os.path.join(output_dir, "oci_subscriptions_combined.csv")
    comm_csv_path = os.path.join(output_dir, "oci_subscription_commitments.csv")

    # Keep your existing columns as-is to avoid DB changes on the main table.
    subs_fields = [
        "subscription_id", "iso_code", "name", "std_precision",
        "service_name", "status", "available_amount", "booking_opty_number",
        #"commitment_services", 
        "csi", "data_center_region", "funded_allocation_value",
        "id", "is_intent_to_pay", "net_unit_price", "operation_type", "order_number",
        "original_promo_amount", "partner_transaction_type", "pricing_model",
        "product_name", "product_part_number", "product_provisioning_group",
        "product_unit_of_measure", "program_type", "promo_type", "quantity", "substatus",
        "time_end", "time_start", "total_value", "used_amount"
    ]

    # New normalized commitments table columns
    comm_fields = [
        "SUBSCRIPTION_ID",
        "SUBSCRIPTION_LINE_ID",
        "COMMITMENT_TIME_START",
        "COMMITMENT_TIME_END",
        "COMMITMENT_QUANTITY",
        "COMMITMENT_AVAILABLE_AMT",
        "COMMITMENT_LINE_NET_AMT",
        "COMMITMENT_FA_VALUE"
    ]

    client = oci.onesubscription.SubscriptionClient(config={}, signer=signer)

    with open(subs_csv_path, "w", newline="", encoding="utf-8") as f_subs, \
         open(comm_csv_path, "w", newline="", encoding="utf-8") as f_comm:

        subs_writer = csv.DictWriter(f_subs, fieldnames=subs_fields)
        comm_writer = csv.DictWriter(f_comm, fieldnames=comm_fields)
        subs_writer.writeheader()
        comm_writer.writeheader()

        for subscription_id in subscription_ids:
            try:
                logging.info(f"📦 Fetching data for subscription: {subscription_id}")
                resp = client.list_subscriptions(
                    compartment_id=tenancy_id,
                    subscription_id=subscription_id,
                    is_commit_info_required=True   # <-- key change
                )
                subs = resp.data

                for sub in subs:
                    # Subscribed services array (can be None)
                    for svc in (getattr(sub, "_subscribed_services", None) or [None]):
                        # Main table row (unchanged schema)
                        row = {
                            "subscription_id": subscription_id,
                            "iso_code": getattr(getattr(sub, "_currency", None), "iso_code", "") if getattr(sub, "_currency", None) else "",
                            "name": getattr(getattr(sub, "_currency", None), "name", "") if getattr(sub, "_currency", None) else "",
                            "std_precision": getattr(getattr(sub, "_currency", None), "std_precision", "") if getattr(sub, "_currency", None) else "",
                            "service_name": getattr(sub, "_service_name", "") or "",
                            "status": getattr(sub, "_status", "") or "",
                            "available_amount": getattr(svc, "available_amount", "") if svc else "",
                            "booking_opty_number": getattr(svc, "booking_opty_number", "") if svc else "",
                            #"commitment_services": getattr(svc, "commitment_services", "") if svc else "",
                            "csi": getattr(svc, "csi", "") if svc else "",
                            "data_center_region": getattr(svc, "data_center_region", "") if svc else "",
                            "funded_allocation_value": getattr(svc, "funded_allocation_value", "") if svc else "",
                            "id": getattr(sub, "id", "") if hasattr(sub, 'id') else "",
                            "is_intent_to_pay": getattr(svc, "is_intent_to_pay", "") if svc else "",
                            "net_unit_price": getattr(svc, "net_unit_price", "") if svc else "",
                            "operation_type": getattr(svc, "operation_type", "") if svc else "",
                            "order_number": getattr(svc, "order_number", "") if svc else "",
                            "original_promo_amount": getattr(svc, "original_promo_amount", "") if svc else "",
                            "partner_transaction_type": getattr(svc, "partner_transaction_type", "") if svc else "",
                            "pricing_model": getattr(svc, "pricing_model", "") if svc else "",
                            "product_name": getattr(getattr(svc, "product", None), "name", "") if (svc and getattr(svc, "product", None)) else "",
                            "product_part_number": getattr(getattr(svc, "product", None), "part_number", "") if (svc and getattr(svc, "product", None)) else "",
                            "product_provisioning_group": getattr(getattr(svc, "product", None), "provisioning_group", "") if (svc and getattr(svc, "product", None)) else "",
                            "product_unit_of_measure": getattr(getattr(svc, "product", None), "unit_of_measure", "") if (svc and getattr(svc, "product", None)) else "",
                            "program_type": getattr(svc, "program_type", "") if svc else "",
                            "promo_type": getattr(svc, "promo_type", "") if svc else "",
                            "quantity": getattr(svc, "quantity", "") if svc else "",
                            "substatus": getattr(svc, "status", "") if svc else "",
                            "time_end": getattr(getattr(svc, "time_end", None), "isoformat", lambda: "")() if (svc and getattr(svc, "time_end", None)) else "",
                            "time_start": getattr(getattr(svc, "time_start", None), "isoformat", lambda: "")() if (svc and getattr(svc, "time_start", None)) else "",
                            "total_value": getattr(svc, "total_value", "") if svc else "",
                            "used_amount": getattr(svc, "used_amount", "") if svc else "",
                        }
                        subs_writer.writerow(row)

                        # --- NEW: write one row per commitment to the commitments CSV
                        if svc and getattr(svc, "commitment_services", None):
                            # Ensure SUBSCRIPTION_LINE_ID is present to satisfy NOT NULL
                            svc_line_id = getattr(svc, "id", None)
                            if not svc_line_id:
                                logging.warning(
                                    f"Skipping commitments for subscription {subscription_id}: "
                                    f"no subscribed-service id present (SUBSCRIPTION_LINE_ID is NOT NULL)."
                                )
                            else:
                                for c in (svc.commitment_services or []):
                                    comm_writer.writerow({
                                        "SUBSCRIPTION_ID": subscription_id,
                                        "SUBSCRIPTION_LINE_ID": svc_line_id,
                                        # write ISO strings; we'll parse back to datetime before insert
                                        "COMMITMENT_TIME_START": getattr(getattr(c, "time_start", None), "isoformat", lambda: "")() if getattr(c, "time_start", None) else "",
                                        "COMMITMENT_TIME_END":   getattr(getattr(c, "time_end", None), "isoformat",   lambda: "")() if getattr(c, "time_end", None)   else "",
                                        "COMMITMENT_QUANTITY":               getattr(c, "quantity", ""),
                                        "COMMITMENT_AVAILABLE_AMT":          getattr(c, "available_amount", ""),
                                        "COMMITMENT_LINE_NET_AMT":           getattr(c, "line_net_amount", ""),
                                        "COMMITMENT_FA_VALUE":               getattr(c, "funded_allocation_value", "")
                                    })

            except Exception as e:
                logging.error(f"❌ Failed to fetch subscription {subscription_id}: {e}")

    logging.info(f"✅ All subscription data written to: {subs_csv_path}")
    logging.info(f"✅ All commitment data written to: {comm_csv_path}")
    return subs_csv_path, comm_csv_path

# ---- Loaders ----------------------------------------------------------------
def upload_csv_to_oracle(csv_path, table_name=oci_subscriptions_table):
    os.environ['TNS_ADMIN'] = wallet_path
    conn = None
    cursor = None
    try:
        conn = oracledb.connect(
            user=db_user,
            password=get_secret_value(config["db_credentials"]["pass_secret_ocid"], signer),
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
            if rows:
                cursor.executemany(insert_sql, rows)
                conn.commit()
            logging.info(f"✅ Inserted {cursor.rowcount if rows else 0} rows into {table_name}")

    except Exception as e:
        logging.error(f"❌ Error uploading CSV to Oracle DB ({table_name}): {e}")

    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

def upload_commitments_to_oracle(comm_csv_path, table_name=oci_commitments_table):
    os.environ['TNS_ADMIN'] = wallet_path
    conn = None
    cursor = None
    try:
        conn = oracledb.connect(
            user=db_user,
            password=get_secret_value(config["db_credentials"]["pass_secret_ocid"], signer),
            dsn=db_dsn
        )
        cursor = conn.cursor()
        cursor.execute(f"TRUNCATE TABLE {table_name}")
        logging.info(f"Cleared existing data from {table_name}")

        with open(comm_csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            cols = reader.fieldnames  # should match comm_fields above exactly

            # Convert timestamp strings to datetime objects for TIMESTAMP(6) columns
            def to_dt(val):
                if not val:
                    return None
                # Handles "YYYY-MM-DDTHH:MM:SS[.ffffff][+TZ]" — we ignore timezone if present.
                try:
                    # Prefer fromisoformat; strip timezone if necessary (Oracle TIMESTAMP(6) is naive)
                    # Split off timezone part if present
                    base = val.split("+")[0].split("Z")[0]
                    return datetime.fromisoformat(base)
                except Exception:
                    # Fallback: try a couple of common masks
                    for mask in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
                        try:
                            return datetime.strptime(val, mask)
                        except Exception:
                            pass
                    logging.warning(f"Could not parse timestamp '{val}', inserting NULL.")
                    return None

            rows = []
            for row in reader:
                row = dict(row)  # copy
                row["COMMITMENT_TIME_START"] = to_dt(row.get("COMMITMENT_TIME_START", ""))
                row["COMMITMENT_TIME_END"]   = to_dt(row.get("COMMITMENT_TIME_END", ""))
                rows.append(tuple(row[c] for c in cols))

            if rows:
                placeholders = ", ".join([f":{i+1}" for i in range(len(cols))])
                insert_sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({placeholders})"
                cursor.executemany(insert_sql, rows)
                conn.commit()

            logging.info(f"✅ Inserted {cursor.rowcount if rows else 0} rows into {table_name}")

    except Exception as e:
        logging.error(f"❌ Error uploading commitments CSV to Oracle DB ({table_name}): {e}")

    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

# ---- MAIN -------------------------------------------------------------------
if __name__ == "__main__":
    sub_ids = get_all_subscription_ids()
    logging.info(f"Found {len(sub_ids)} subscriptions.")
    csv_subs, csv_comm = list_all_subscriptions(sub_ids)

    # Load main (existing) table
    if csv_subs:
        upload_csv_to_oracle(csv_subs, table_name=oci_subscriptions_table)

    # Load new commitments child table
    if csv_comm:
        upload_commitments_to_oracle(csv_comm, table_name=oci_commitments_table)

    # Call your procedures
    try:
        os.environ['TNS_ADMIN'] = wallet_path
        db_password = get_secret_value(config["db_credentials"]["pass_secret_ocid"], signer) \
            if not use_test_creds else db_pass

        with oracledb.connect(user=db_user, password=db_password, dsn=db_dsn) as final_conn:
            final_cursor = final_conn.cursor()
            log_and_execute(final_cursor, "BEGIN UPDATE_OCI_SUBSCRIPTION_DETAILS; END;")
            log_and_execute(final_cursor, "BEGIN refresh_credit_consumption_state_proc; END;")
            final_conn.commit()
            final_cursor.close()
            logging.info("✅ Procedures executed successfully.")
    except Exception as e:
        logging.error(f"❌ Failed to execute post-load procedures: {e}")