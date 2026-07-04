from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category
from app.schemas import CategoryOut

router = APIRouter()


def _build_tree(categories: list[Category], parent_id: int | None = None) -> list[dict]:
    result = []
    for cat in categories:
        if cat.parent_id == parent_id:
            node = CategoryOut.model_validate(cat).model_dump()
            node["children"] = _build_tree(categories, cat.id)
            result.append(node)
    return result


@router.get("")
def list_categories(db: Session = Depends(get_db)):
    cats = (
        db.query(Category)
        .filter(Category.is_active == 1)
        .order_by(Category.sort_order, Category.name_en)
        .all()
    )
    return _build_tree(cats, parent_id=None)
