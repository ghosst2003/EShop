from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_admin
from app.models import Product, ProductReview, ReviewModeration, User

router = APIRouter()


class ReviewDecision(BaseModel):
    status: str
    merchant_reply: Optional[str] = Field(default=None, max_length=2000)


def as_row(review, moderation):
    return {
        "id": review.id, "product_id": review.product_id,
        "product_title": getattr(review, "product_title", None),
        "reviewer_name": review.buyer.display_name or review.buyer.username,
        "rating": review.rating, "title": review.title, "comment": review.comment,
        "verified_purchase": bool(review.verified_purchase), "created_at": review.created_at,
        "status": moderation.status if moderation else "approved",
        "merchant_reply": moderation.merchant_reply if moderation else None,
    }


@router.get("")
def list_reviews(status: Optional[str] = Query(None), db: Session = Depends(get_db), _admin: User = Depends(get_current_admin)):
    reviews = db.query(ProductReview).options(joinedload(ProductReview.buyer)).order_by(ProductReview.created_at.desc()).all()
    product_titles = dict(db.query(Product.id, Product.title_en).filter(Product.id.in_([r.product_id for r in reviews])).all()) if reviews else {}
    mods = {m.review_id: m for m in db.query(ReviewModeration).filter(ReviewModeration.review_id.in_([r.id for r in reviews])).all()} if reviews else {}
    result = []
    for review in reviews:
        row = as_row(review, mods.get(review.id)); row["product_title"] = product_titles.get(review.product_id)
        if not status or row["status"] == status: result.append(row)
    return result


@router.put("/{review_id}")
def moderate_review(review_id: int, data: ReviewDecision, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    if data.status not in {"pending", "approved", "rejected"}: raise HTTPException(status_code=400, detail="Invalid review status")
    review = db.query(ProductReview).filter(ProductReview.id == review_id).first()
    if not review: raise HTTPException(status_code=404, detail="Review not found")
    row = db.query(ReviewModeration).filter(ReviewModeration.review_id == review.id).first()
    if not row:
        row = ReviewModeration(review_id=review.id); db.add(row)
    row.status = data.status; row.merchant_reply = data.merchant_reply; row.moderated_by = admin.id; row.moderated_at = datetime.utcnow()
    db.commit(); db.refresh(row)
    return as_row(review, row)
