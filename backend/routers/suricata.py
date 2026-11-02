import json
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import LogEvent
from redis_client import r

router = APIRouter(prefix="/suricata", tags=["Suricata Ingestion"])
SURICATA_LOCK_KEY = "lock:suricata_ingestion"

@router.post("/ingest-logs", status_code=status.HTTP_200_OK)
def ingest_suricata_logs(log_file_path: str = "/var/log/suricata/eve.json", db: Session = Depends(get_db)):
    acquired = r.set(SURICATA_LOCK_KEY, "running", nx=True, ex=300)
    if not acquired:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A Suricata log ingestion process is already running."
        )

    if not os.path.exists(log_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Suricata log file not found at path: {log_file_path}"
        )

    try:
        ingested_count = 0
        batch_records = []
        BATCH_SIZE = 500  # Commit in chunks to prevent memory overhead and database locks

        with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line_stripped = line.strip()
                if not line_stripped:
                    continue
                try:
                    event = json.loads(line_stripped)
                except json.JSONDecodeError:
                    continue

                # Process only alert-type events from Suricata
                if event.get("event_type") == "alert":
                    alert_info = event.get("alert", {})
                    
                    ocsf_payload = {
                        "class_uid": 4001,  # OCSF Network Activity / Intrusion Finding
                        "category_uid": 4,
                        "severity": alert_info.get("severity", 3),
                        "network_activity": {
                            "src_ip": event.get("src_ip"),
                            "dest_ip": event.get("dest_ip"),
                            "signature": alert_info.get("signature"),
                            "category": alert_info.get("category")
                        },
                        "metadata": {
                            "product": {"name": "Suricata", "vendor_name": "OISF"},
                            "profiles": ["Network", "IDS"]
                        }
                    }

                    batch_records.append(
                        LogEvent(
                            class_uid=4001,
                            category_uid=4,
                            severity=str(alert_info.get("severity", "Medium")),
                            raw_payload=ocsf_payload
                        )
                    )
                    ingested_count += 1

                    # Batch write to keep memory clean and prevent transaction locking
                    if len(batch_records) >= BATCH_SIZE:
                        db.bulk_save_objects(batch_records)
                        db.commit()
                        batch_records.clear()

        # Flush any remaining records outside the batch size limit
        if batch_records:
            db.bulk_save_objects(batch_records)
            db.commit()

        return {
            "status": "success",
            "message": "Suricata logs successfully parsed and bulk ingested.",
            "ingested_count": ingested_count
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
    
    finally:
        r.delete(SURICATA_LOCK_KEY)