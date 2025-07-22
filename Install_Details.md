
# 🔧 OCI Focus Reports – Quick Deployment Guide

## 1. 🖥️ VM Setup & Initialization

### Check Cloud Init Script
```bash
tail -f /var/log/cloud-init-output.log
```
> Wait until completion. Once successful, **relogin** to the VM.

---

## 2. 📁 Navigate to Script Directory
```bash
cd /home/opc/oci-focus-reports/db_scripts
```

---

## 3. 🛠️ Install Database Components

### 3.1 Create APEX Workspace
```bash
sqlplus admin@fcradw_high @create_apex_workspace.sql
```

### 3.2 Install DB Objects
```bash
sqlplus oci_focus_reports@fcradw_high @install_ov_db_objects.sql
```

### 3.3 Install APEX Application
```bash
sqlplus oci_focus_reports@fcradw_high @install_ov_apex_app.sql
```

---

## 4. 🔐 Login to APEX Workspace

- **Workspace:** `OCI_FOCUS_REPORTS`  
- **Username:** `OCI_FOCUS_REPORTS`  
- **Password:** `<your_password_used_in_terraform_variables>`

---

## 5. 📦 Run Initial Load Script
```bash
/home/opc/oci-focus-reports/other_scripts/initial_load.sh
```

---

## 6. 📈 Scale Up/Down ADW (Manual Execution)

- **Scale Up**
```bash
/home/opc/oci-focus-reports/other_scripts/scale_up_db.sh
```
> Wait a couple of minutes for scaling to complete.

- **Scale Down**
```bash
/home/opc/oci-focus-reports/other_scripts/scale_down_db.sh
```

---

## 7. ⏲️ Install Cron Jobs
```bash
/home/opc/oci-focus-reports/other_scripts/install_cron.sh
```

---

## 8. 🔑 First-Time Login to OV APEX App

- **Username:** `OVADMIN`  
- **Password:** `Mypassword123123`  
> You will be prompted to change the password on first login.

---

## 9. 🔐 APEX App with IAM Domain SSO

### 9.1 OCI IAM Configuration
1. Login to **OCI Console**
2. Navigate to:  
   **Identity & Security** → **Domains** → *Default Domain*
3. In `Integrated Applications`:
   - Note **Client ID** & **Secret**
   - Click **Edit OAuth Configuration**:
     - **Redirect URL:**  
       `https://<adw_url>/ords/apex_authentication.callback`
     - **Post-logout Redirect URL:**  
       `https://<adw_url>/ords/f?p=100`
4. Note the **Domain URL** from **Default Domain → Details**

### 9.2 IAM Groups
- Admin users should belong to: `CA_APEX_ADMINS`
- All other users: `CA_APEX_USERS`

---

## 10. ⚙️ Configure APEX App for SSO

### 10.1 Web Credentials
- Path: `Workspace Utilities` → `Web Credentials`
- Edit: `OCI OAuth Credentials`  
  → Update **Client ID** & **Secret**

### 10.2 Authentication Scheme
- Path: `App Builder` → `Shared Components` → `Authentication Schemes`
- Edit `OCI IAM OAuth`:
  - Set **Discovery URL**:  
    `https://<domain_url>/.well-known/openid-configuration`
  - Click: **Make Current Scheme**

### 10.3 Authorization Schemes

#### Administration Rights
```sql
select 1 from APEX_WORKSPACE_SESSION_GROUPS
where apex_session_id = :app_session
and group_name in ('CA_APEX_ADMINS')
```

#### Contribution Rights
```sql
select 1 from APEX_WORKSPACE_SESSION_GROUPS
where apex_session_id = :app_session
and group_name in ('CA_APEX_ADMINS')
```

---

## 11. 🧾 Application Setup Steps

### 11.1 Edit "Current Active Orders"
- Login to App
- Go to: `Edit Tables` → `Current Active Orders`
- Update **Order Name** to friendly labels  
- Click **Save**

### 11.2 Add Workloads
- Path: `Edit Tables` → `Workloads` → `Add Workload`
- Fill in required details (environment, customer, etc.)
- Submit each workload
- After adding, click **Refresh DB Tables`

> These workloads help in grouping compartments for cost analysis by workload, customer, or environment.
