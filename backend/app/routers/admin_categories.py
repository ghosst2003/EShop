from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Category, OperationLog
from app.schemas import CategoryCreate, CategoryUpdate, CategoryOut

router = APIRouter()


def _log_action(db: Session, user: User, action: str, entity_type: str, entity_id: int | None, details: dict | None):
    log = OperationLog(
        user_id=user.id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    db.add(log)
    db.commit()


@router.get("", response_model=list[CategoryOut])
def list_categories(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return (
        db.query(Category)
        .order_by(Category.sort_order, Category.name)
        .all()
    )


@router.post("", response_model=CategoryOut)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    existing = db.query(Category).filter(Category.slug == data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")
    cat = Category(
        parent_id=data.parent_id,
        name=data.name,
        name_en=data.name_en,
        slug=data.slug,
        description=data.description,
        icon=data.icon,
        sort_order=data.sort_order,
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    _log_action(db, user, "create", "category", cat.id, {"name": data.name})
    return cat


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, field, value)
    db.commit()
    db.refresh(cat)
    _log_action(db, user, "update", "category", category_id, data.model_dump(exclude_unset=True))
    return cat


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
    _log_action(db, user, "delete", "category", category_id, None)
    return {"message": "Category deleted"}
