from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ---- GDPR ----
class GdprConsentRequest(BaseModel):
    session_id: str
    consent_type: str  # cookie / newsletter / data_processing
    consent_given: bool


class GdprDataRequest(BaseModel):
    email: str
    request_type: str  # data_export / data_deletion / rectification
    details: Optional[str] = None


class GdprRequestOut(BaseModel):
    id: int
    email: str
    request_type: str
    details: Optional[str] = None
    status: str
    admin_notes: Optional[str] = None
    processed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class GdprRequestStatusUpdate(BaseModel):
    status: str  # pending / in_progress / completed / rejected
    admin_notes: Optional[str] = None
