Cybersecurity Tools ingestion and dashboards 

Use the open source alternatives for Enterprise level Cyber security tools 

## 🛠️ Enterprise to Open-Source Security Mapping

To build this platform without relying on expensive, proprietary corporate vendor licenses, the following production-grade open-source tools were selected to replicate enterprise capabilities:

| Corporate Enterprise Tool | Core Functional Domain | Free Open-Source Alternative |
| :--- | :--- | :--- |
| Qualys / Ionix | Vulnerability Scanning & Asset Discovery | Trivy / OWASP ZAP |
| Archer / Armorcode | Aggregation & Risk Management (ASPM) | DefectDojo |
| Bitsight | Compliance Ratings & Threat Intelligence | OpenCVE |
| Zscaler | Secure Web Gateway & Network Inspection | Suricata Logs / Squid |

### 🚀 Architectural Implementation
1. **Data Ingestion:** The backend utilizes CLI inputs from **Trivy** to generate raw JSON security vulnerability reports.
2. **Aggregation:** A custom **FastAPI / Node.js** processing engine parses raw findings, deduplicates vectors, and stores active threats inside a relational database.
3. **Visualization:** A **React.js** web interface acts as the local governance panel, simulating dashboard features typically found in enterprise risk management platforms.


## 🏗️ Managed Asset Architecture

The platform categorizes and tracks three core types of infrastructure and application assets within the database schema to simulate an enterprise risk perimeter:

| Asset Classification | Real-World Example | Simulated Database Context |
| :--- | :--- | :--- |
| **Application Assets** | Source Code Repositories | Git repositories (`payment-api`, `auth-service`) |
| **Artifact Assets** | Container Images | Docker registry tags (`node:18-alpine`, `python:3.10`) |
| **Cloud Infrastructure** | Cloud Storage & Networks | AWS/Azure resources (`finance-s3-bucket`, `prod-vpn`) |

### 📊 Database Schema Design (Asset Payload Example)
Assets are tracked as JSON documents or relational rows containing risk levels and real-time vulnerability counts. When a security scanner runs, it maps findings directly to these specific asset records:

```json
{
  "asset_id": "ASSET-102",
  "asset_name": "wealth-management-api",
  "asset_type": "Code Repository",
  "environment": "Production",
  "criticality_tier": "High",
  "active_vulnerabilities": {
    "critical": 2,
    "high": 5,
    "medium": 12
  },
  "last_scanned_at": "2026-08-18T22:45:00Z"
}
```

Trivy - use national vuln database cve 