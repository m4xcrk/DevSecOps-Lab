# 🚀 Automated 4-Node DevSecOps & Security Operations (SOC) Lab

A production-grade, distributed DevSecOps infrastructure framework deployed inside **LXD/LXC system containers** on an **ARM64 (Apple Silicon)** architecture. The laboratory environment is fully managed via a macOS Control Plane using **Infrastructure as Code (IaC)** and **Configuration Management** tools, providing automated software pipeline delivery alongside real-time security telemetry capture.

---

## 🏗️ Lab Architecture Topology

The entire environment shares a dedicated host private bridge network interface mapping static private network ranges.

[ macOS Control Plane ] (Intel/M-Series Host)│▼  (Static Native Routing Policy via Bridge Interface)┌──────────────────────────────────────────────────────────┐│                  Ubuntu Server (LXD Engine Host)         │├──────────────┬──────────────┬──────────────┬─────────────┤│   VM-001     │   VM-002     │   VM-003     │   VM-004    ││  Nginx LB    │ DevOps Node  │  Attack Lab  │  SIEM Brain ││ 10.69.98.11  │ 10.69.98.12  │ 10.69.98.13  │ 10.69.98.14 │└──────┬───────┴──────┬───────┴──────┬───────┴──────┬──────┘│              │              │              │Wazuh Agent-1  Wazuh Agent-2  Wazuh Agent-3  Wazuh Manager (SIEM)


### 🛰️ Container Cluster Node Assignments


| Instance ID | Role / Assignment | IP Endpoint | Core Running Configurations | Telemetry Type |
| :--- | :--- | :--- | :--- | :--- |
| **VM-001** | **Nginx Edge LB** | `10.69.98.11` | Reverse Proxy Engine, SSL Termination Routing | Wazuh Agent-1 |
| **VM-002** | **DevOps Hub** | `10.69.98.12` | Remote Docker Engine API v1.52, Prometheus, Grafana | Wazuh Agent-2 |
| **VM-003** | **Attack Lab** | `10.69.98.13` | Auditing Matrix suites (Nmap, Hydra, Nikto, Dirb) | Wazuh Agent-3 |
| **VM-004** | **SOC SIEM Core** | `10.69.98.14` | Docker-Engine nested instance, **Wazuh Core v4.14.5** | Wazuh Manager |

---

## 🛠️ Automated Technical Stack Architecture

*   **Host Virtualization Layer:** Canonical LXD/LXC (Privileged Nesting Enabled)
*   **Infrastructure Management:** Terraform (Remote Docker Provider Registry v2.25.0)
*   **Automation Blueprinting:** Ansible Playbooks Ad-hoc Deployment
*   **Metrics Telemetry & Dashboards:** Prometheus Engine & Grafana Analytical Metrics
*   **Threat Detection Matrix:** Wazuh Distributed Architecture Core (Single-Node Stack)

---

## 🚀 Step-by-Step Installation Framework

### 1. Persistent Routing Configuration (macOS Host Control Plane)
Because Mac native static routes clear out automatically during a hard power restart, load this persistent route launch policy statement structure:
```bash
sudo route -n add 10.69.98.0/24 10.211.55.5
```

### 2. Remote Docker Hub Provisoning via IaC
To manage the target runtime from the control plane using the correct engine API socket configuration parameters, execute:
```bash
export DOCKER_API_VERSION=1.52
terraform init
terraform apply -auto-approve
```

### 3. Edge Reverse Proxy Routing Definitions (`/etc/nginx/sites-available/default`)
The load balancer directs all public HTTP traffic inbound to respective nodes seamlessly down to localized port boundaries:
```nginx
server {
    listen 80;

    location /wazuh/ {
        proxy_pass https://10.69.98;
        proxy_ssl_verify off;
    }
    location /grafana/ {
        proxy_pass http://10.69.98;
    }
    location /prometheus/ {
        proxy_pass http://10.69.98;
    }
}
```

---

## 📉 Low-Resource Architecture Optimizations (3GB RAM Profile)
Running standard Elasticsearch/OpenSearch-based stacks inside constrained testing containers requires strategic performance engineering definitions applied directly into `docker-compose.yml`:

*   **JVM Heap Limitation:** Java memory footprints forced down to maximize resources:
    `OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m -Dopensearch.check_all_nodes=false`
*   **Memory Management Policy:** Bypassed restrictive host calls inside container boundaries:
    `bootstrap.memory_lock=false`
*   **Single Node Convergence Enforcements:**
    `discovery.type=single-node`

---

## 🛡️ Defensive Engineering Simulation Matrix (MITRE ATT&CK)

The environment includes predefined scenarios to validate active warning detections against the `alerts.log` framework engine on the SIEM Master node.

### A. Network Discovery Reconnaissance (Technique T1046)
Execute an intrusive service footprint lookup mapping from the Attack container (**VM-003**) targeting production nodes directly:
```bash
lxc exec VM-003 -- nmap -A -T4 10.69.98.12
```
*   **Expected Event ID Capture:** Rule `5101` (Network scan alert triggered).

### B. Unprivileged Credential Brute Force (Technique T1110)
Simulate a rapid online password spray session from the offensive console node:
```bash
lxc exec VM-003 -- hydra -l root -p wrongpassword123 10.69.98.12 ssh
```
*   **Expected Event ID Capture:** Rule `5710` / `5712` (SSH login validation failure sequence).

### C. Local Privilege Escalation Trigger (Technique T1548.001)
Simulate unauthorized shadow credential manipulation directly within the production compute stack:
```bash
lxc exec VM-002 -- bash -c "sudo cat /etc/shadow"
```
*   **Expected Event ID Capture:** Rule `5403` (*First time user executed sudo* logged immediately via journald).

### D. Malicious Payload Dropper Execution (Technique T1566)
Drop an EICAR analytical test string inside temporal tracking lines to trigger specific validation pipelines:
```bash
lxc exec VM-002 -- bash -c 'echo "X5O!P%@AP[4\PZX54(P^)7CC)7}\$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!\$H+H*" > /tmp/virus_test.txt'
```

---

## 💾 Maintenance & Administration

To inspect SAN backend tracking statistics to make sure items stay under standard storage allocations, execute:
```bash
lxc storage info SAN
```

To review logging streams generated across target instances straight from the manager, stream the central alert log:
```bash
lxc exec VM-004 -- docker exec single-node-wazuh.manager-1 tail -f /var/ossec/logs/alerts/alerts.log
```

---

### 👤 Laboratory Administrator
*   **Maintainer Profile:** **m4xcrk**
*   **Project Context:** Continuous DevSecOps Framework Evaluation Lab Environment
