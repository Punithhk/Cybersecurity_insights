from fastapi import FastAPI, HTTPException,Body
from routers import trivy, opencve, suricata
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests
import os

load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

app = FastAPI(title="Mini-Splunk Ingestion Engine", version="1.0.0", description="A lightweight ingestion engine for OCSF-compliant logs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trivy.router, prefix="/api/v1", tags=["Trivy Ingestion"])
app.include_router(opencve.router, prefix="/api/v1", tags=["OpenCVE Ingestion"])
app.include_router(suricata.router, prefix="/api/v1", tags=["Suricata Ingestion"])

@app.post("/api/auth/google")
async def google_auth(payload: dict = Body(...)):
    cred = payload.get("credential")
    if not cred:
        raise HTTPException(status_code=400, detail="Missing cred token")

    try:
        user_info = id_token.verify_oauth2_token(
            cred,
            requests.Request(),
            CLIENT_ID
        )
        print(user_info)
        if user_info['iss'] not in ['accounts.google.com','https://accounts.google.com']:
            raise ValueError('Wrong issuer')

    except Exception as e:
        raise HTTPException(status_code=401, detail=f'Invalid Google Token: {str(e)}')

    return {
        "message":"Login successful",
        "user":{
           "email": user_info.get("email"),
            "name": user_info.get("name"),
            "picture": user_info.get("picture"),
            "id": user_info.get("sub") # Unique Google User ID 
        }
    }


@app.get("/")
def welcome():
    return {"status":"running"}

@app.get("/health")
def health_check():
    return {"status": "running", "message": "Mini-Splunk backend is active"}