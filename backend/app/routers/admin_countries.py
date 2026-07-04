from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Country
from app.schemas import CountryCreate, CountryOut

router = APIRouter()


@router.get("", response_model=list[CountryOut])
def list_countries(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """获取所有国家列表（按 sort_order 排序）"""
    return db.query(Country).filter(Country.is_active == 1).order_by(Country.sort_order).all()


@router.post("", response_model=CountryOut)
def create_country(
    data: CountryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """新增国家"""
    existing = db.query(Country).filter(Country.code == data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"国家代码 {data.code} 已存在")
    country = Country(**data.model_dump())
    db.add(country)
    db.commit()
    db.refresh(country)
    return country


@router.put("/{country_id}", response_model=CountryOut)
def update_country(
    country_id: int,
    data: CountryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """更新国家"""
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(country, field, value)
    db.commit()
    db.refresh(country)
    return country


@router.delete("/{country_id}")
def delete_country(
    country_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """软删除国家（设置 is_active = 0）"""
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    country.is_active = 0
    db.commit()
    return {"message": "Country deactivated"}
