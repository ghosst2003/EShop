from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Order, OrderItem, Product, ProductReview, User, WishlistItem
from app.schemas import ReviewCreate, ReviewOut, ReviewsSummary, SavedProductOut

router = APIRouter()


@router.get("/promotions/{code}")
def validate_promotion(code: str):
    if code.strip().upper() != "WELCOME10":
        raise HTTPException(status_code=404, detail="This promotion code is not valid")
    return {
        "code": "WELCOME10",
        "label": "Welcome offer",
        "discount_type": "percent",
        "discount_value": 10,
    }


def _buyer_only(user: User):
    if user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can use this feature")


@router.get("/saved-products", response_model=list[SavedProductOut])
def list_saved_products(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _buyer_only(user)
    return (
        db.query(WishlistItem)
        .options(joinedload(WishlistItem.product).joinedload(Product.images))
        .filter(WishlistItem.buyer_id == user.id)
        .order_by(WishlistItem.created_at.desc())
        .all()
    )


@router.post("/saved-products/{product_id}", response_model=SavedProductOut)
def save_product(product_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _buyer_only(user)
    product = db.query(Product).filter(Product.id == product_id, Product.status == "active").first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    item = db.query(WishlistItem).filter(
        WishlistItem.buyer_id == user.id,
        WishlistItem.product_id == product_id,
    ).first()
    if not item:
        item = WishlistItem(buyer_id=user.id, product_id=product_id)
        db.add(item)
        db.commit()
    return (
        db.query(WishlistItem)
        .options(joinedload(WishlistItem.product).joinedload(Product.images))
        .filter(WishlistItem.buyer_id == user.id, WishlistItem.product_id == product_id)
        .first()
    )


@router.delete("/saved-products/{product_id}", status_code=204)
def unsave_product(product_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _buyer_only(user)
    item = db.query(WishlistItem).filter(
        WishlistItem.buyer_id == user.id,
        WishlistItem.product_id == product_id,
    ).first()
    if item:
        db.delete(item)
        db.commit()


@router.get("/products/{product_id}/reviews", response_model=ReviewsSummary)
def list_product_reviews(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product.id).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    rows = (
        db.query(ProductReview)
        .options(joinedload(ProductReview.buyer))
        .filter(ProductReview.product_id == product_id)
        .order_by(ProductReview.created_at.desc())
        .all()
    )
    distribution = {rating: 0 for rating in range(1, 6)}
    for row in rows:
        distribution[row.rating] += 1
    average = round(sum(row.rating for row in rows) / len(rows), 1) if rows else 0
    return ReviewsSummary(
        average_rating=average,
        review_count=len(rows),
        rating_distribution=distribution,
        reviews=[
            ReviewOut(
                id=row.id,
                rating=row.rating,
                title=row.title,
                comment=row.comment,
                reviewer_name=row.buyer.display_name or row.buyer.username,
                verified_purchase=bool(row.verified_purchase),
                created_at=row.created_at,
            )
            for row in rows
        ],
    )


@router.post("/products/{product_id}/reviews", response_model=ReviewOut)
def submit_product_review(
    product_id: int,
    data: ReviewCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _buyer_only(user)
    if not db.query(Product.id).filter(Product.id == product_id).first():
        raise HTTPException(status_code=404, detail="Product not found")
    verified = bool(
        db.query(OrderItem.id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(
            Order.buyer_id == user.id,
            OrderItem.product_id == product_id,
            Order.status.in_(["paid", "shipped", "completed"]),
        )
        .first()
    )
    row = db.query(ProductReview).filter(
        ProductReview.buyer_id == user.id,
        ProductReview.product_id == product_id,
    ).first()
    if row:
        row.rating = data.rating
        row.title = data.title
        row.comment = data.comment
        row.verified_purchase = int(verified)
    else:
        row = ProductReview(
            buyer_id=user.id,
            product_id=product_id,
            rating=data.rating,
            title=data.title,
            comment=data.comment,
            verified_purchase=int(verified),
        )
        db.add(row)
    db.commit()
    db.refresh(row)
    return ReviewOut(
        id=row.id,
        rating=row.rating,
        title=row.title,
        comment=row.comment,
        reviewer_name=user.display_name or user.username,
        verified_purchase=verified,
        created_at=row.created_at,
    )
