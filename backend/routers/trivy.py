import subprocess
import json
import tempfile
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models  import LogEvent
from redis_client import r

router = APIRouter(prefix="/trivy", tags=["Trivy Ingestion"])
TRIVY_LOCK_KEY = "lock:trivy_ingestion"

@router.post("/scan-local", status_code=status.HTTP_200_OK)
def scan_local_project(target_path: str = ".", db: Session = Depends(get_db)):
    # Lock is exclusive ONLY to Trivy; OpenCVE can still run simultaneously
    acquired = r.set(TRIVY_LOCK_KEY, "running", nx=True, ex=300)
    if not acquired:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A Trivy scan is already in progress. Please wait."
        )

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            tmp_filename = tmp.name

        cmd = ["trivy", "fs", "--format", "json", "--output", tmp_filename, target_path]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Trivy failed: {result.stderr}")

        with open(tmp_filename, "r") as f:
            scan_data = json.load(f)

        os.unlink(tmp_filename)

        ingested_count = 0
        for target_result in scan_data.get("Results", []) or []:
            for vuln in target_result.get("Vulnerabilities", []) or []:
                cve_id = vuln.get("VulnerabilityID")
                severity = vuln.get("Severity", "UNKNOWN")
                
                ocsf_payload = {
                    "class_uid": 2002,
                    "category_uid": 2,
                    "severity": severity,
                    "vulnerability": {"uid": cve_id, "package": vuln.get("PkgName")},
                    "metadata": {"product": {"name": "Trivy", "vendor_name": "Aqua Security"}, "profiles": ["Software"]}
                }

                db_log = LogEvent(class_uid=2002, category_uid=2, severity=severity, raw_payload=ocsf_payload)
                db.add(db_log)
                ingested_count += 1

        db.commit()
        return {"status": "success", "ingested_count": ingested_count}

    finally:
        r.delete(TRIVY_LOCK_KEY)

