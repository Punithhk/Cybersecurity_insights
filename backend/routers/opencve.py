import requests
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from database import get_db
from models import LogEvent
from redis_client import r
from schemas import IngestTriggerRequest

router = APIRouter(prefix="/opencve", tags=["OpenCVE Ingestion"])
OPENCVE_LOCK_KEY = "lock:opencve_ingestion"

@router.post("/sync", status_code=status.HTTP_200_OK)
def sync_opencve_data(payload: IngestTriggerRequest, db: Session = Depends(get_db)):
    # Lock is exclusive ONLY to OpenCVE
    acquired = r.set(OPENCVE_LOCK_KEY, "running", nx=True, ex=300)
    
    if not acquired:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An OpenCVE synchronization is already running. Try again later."
        )
    
    try:
        OPENCVE_URL = "https://app.opencve.io/api/v2/cves"
        headers = {"Authorization": f"Bearer {payload.token}", "Accept": "application/json"}
        
        response = requests.get(OPENCVE_URL, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch from OpenCVE: {response.text}")
            
        cves_data = response.json()
        cves = cves_data.get("results", cves_data) if isinstance(cves_data, dict) else cves_data

        ingested_count = 0
        for cve in cves[:10]:
            cve_id = cve.get("cve_id") or cve.get("id")
            summary = cve.get("summary", "No description available")
            
            ocsf_payload = {
                "class_uid": 2002,
                "category_uid": 2,
                "severity": "High",
                "vulnerability": {"uid": cve_id, "description": summary},
                "metadata": {"product": {"name": "OpenCVE", "vendor_name": "OpenCVE"}, "profiles": ["Host", "Security Control"]}
            }

            db_log = LogEvent(
                class_uid=2002,
                category_uid=2,
                severity="High",
                raw_payload=ocsf_payload
            )
            db.add(db_log)
            ingested_count += 1
            
        db.commit()
        
        return {
            "status": "success",
            "message": "OpenCVE ingestion completed successfully.",
            "ingested_count": ingested_count
        }
        
    finally:
        r.delete(OPENCVE_LOCK_KEY)


@router.get("/")
def get_opencve_data():
    # Fetch or return your OCSF-compliant OpenCVE logs
    return [{"id": "1", "severity": "high", "description": "Example vulnerability"}]