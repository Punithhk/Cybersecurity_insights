from pydantic import BaseModel

class IngestTriggerRequest(BaseModel):
    token: str