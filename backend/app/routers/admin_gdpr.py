from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, GdprConsentLog
from app.schemas import GdprRequestOut, GdprRequestStatusUpdate

router = APIRouter()


@router.get("/requests", response_model=list[GdprRequestOut])
def list_gdpr_requests(
    status_filter: str | None = Query(None),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    from app.models import DataDeletionRequest
    q = db.query(DataDeletionRequest).order_by(DataDeletionRequest.created_at.desc())
    if status_filter:
        q = q.filter(DataDeletionRequest.status == status_filter)
    return q.all()


@router.patch("/requests/{request_id}", response_model=GdprRequestOut)
def update_gdpr_request(
    request_id: int,
    data: GdprRequestStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.models import DataDeletionRequest
    dr = db.query(DataDeletionRequest).filter(DataDeletionRequest.id == request_id).first()
    if not dr:
        raise HTTPException(status_code=404, detail="Request not found")
    dr.status = data.status
    dr.admin_notes = data.admin_notes
    dr.processed_by = user.id
    from datetime import datetime
    dr.processed_at = datetime.utcnow()
    db.commit()
    db.refresh(dr)
    return dr


@router.get("/consent-logs")
def list_consent_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    q = db.query(GdprConsentLog).order_by(GdprConsentLog.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [
            {
                "id": i.id,
                "session_id": i.session_id,
                "consent_type": i.consent_type,
                "consent_given": bool(i.consent_given),
                "created_at": i.created_at,
            }
            for i in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
