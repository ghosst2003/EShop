"""Admin: 支付方式管理"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, PaymentMethod
from app.schemas import PaymentMethodCreate, PaymentMethodUpdate, PaymentMethodOut

router = APIRouter()


@router.get("", response_model=list[PaymentMethodOut])
def list_payment_methods(
    db: Session = Depends(get_db),
):
    """获取所有支付方式"""
    return db.query(PaymentMethod).order_by(PaymentMethod.sort_order).all()


@router.post("", response_model=PaymentMethodOut)
def create_payment_method(
    data: PaymentMethodCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """新增支付方式"""
    existing = db.query(PaymentMethod).filter(PaymentMethod.code == data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"支付方式 {data.code} 已存在")

    method = PaymentMethod(**data.model_dump())
    db.add(method)
    db.commit()
    db.refresh(method)
    return method


@router.put("/{method_id}", response_model=PaymentMethodOut)
def update_payment_method(
    method_id: int,
    data: PaymentMethodUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """更新支付方式"""
    method = db.query(PaymentMethod).filter(PaymentMethod.id == method_id).first()
    if not method:
        raise HTTPException(status_code=404, detail="Payment method not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(method, field, value)

    db.commit()
    db.refresh(method)
    return method


@router.delete("/{method_id}")
def delete_payment_method(
    method_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """停用支付方式（设置 is_active = 0）"""
    method = db.query(PaymentMethod).filter(PaymentMethod.id == method_id).first()
    if not method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    method.is_active = 0
    db.commit()
    return {"message": "Payment method deactivated"}


@router.post("/{method_id}/reactivate")
def reactivate_payment_method(
    method_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """重新启用支付方式"""
    method = db.query(PaymentMethod).filter(PaymentMethod.id == method_id).first()
    if not method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    method.is_active = 1
    db.commit()
    db.refresh(method)
    return method
