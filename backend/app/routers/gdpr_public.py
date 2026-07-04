from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GdprConsentLog
from app.schemas import GdprConsentRequest, GdprDataRequest

router = APIRouter()


@router.post("/consent")
def record_consent(
    req: GdprConsentRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    log = GdprConsentLog(
        session_id=req.session_id,
        consent_type=req.consent_type,
        consent_given=1 if req.consent_given else 0,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(log)
    db.commit()
    return {"message": "Consent recorded"}


@router.post("/data-request")
def submit_data_request(
    req: GdprDataRequest,
    db: Session = Depends(get_db),
):
    from app.models import DataDeletionRequest

    dr = DataDeletionRequest(
        email=req.email,
        request_type=req.request_type,
        details=req.details,
    )
    db.add(dr)
    db.commit()
    db.refresh(dr)
    return {"message": "Request submitted", "id": dr.id}
