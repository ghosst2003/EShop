"""收货地址路由 — 买家管理收货地址"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Address
from app.schemas import AddressCreate, AddressUpdate, AddressOut

router = APIRouter()


@router.get("", response_model=list[AddressOut])
def list_addresses(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的所有地址"""
    if user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers have addresses")

    addresses = db.query(Address).filter(Address.buyer_id == user.id).order_by(
        Address.is_default.desc(), Address.updated_at.desc()
    ).all()
    return addresses


@router.post("", response_model=AddressOut, status_code=201)
def create_address(
    data: AddressCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """添加新地址"""
    if user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers have addresses")

    # 如果设为默认，先取消其他默认地址
    if data.is_default:
        db.query(Address).filter(
            Address.buyer_id == user.id, Address.is_default == 1
        ).update({"is_default": 0})

    address = Address(
        buyer_id=user.id,
        label=data.label,
        recipient_name=data.recipient_name,
        phone=data.phone,
        country=data.country,
        city=data.city,
        postal_code=data.postal_code,
        street_address=data.street_address,
        is_default=1 if data.is_default else 0,
    )
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


@router.put("/{address_id}", response_model=AddressOut)
def update_address(
    address_id: int,
    data: AddressUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新地址"""
    if user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers have addresses")

    address = db.query(Address).filter(
        Address.id == address_id, Address.buyer_id == user.id
    ).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    update_data = data.model_dump(exclude_unset=True)

    # 如果设为默认，先取消其他默认地址
    if update_data.get("is_default"):
        db.query(Address).filter(
            Address.buyer_id == user.id,
            Address.is_default == 1,
            Address.id != address_id,
        ).update({"is_default": 0})

    for field, value in update_data.items():
        setattr(address, field, value)

    db.commit()
    db.refresh(address)
    return address


@router.delete("/{address_id}", status_code=204)
def delete_address(
    address_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除地址"""
    if user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers have addresses")

    address = db.query(Address).filter(
        Address.id == address_id, Address.buyer_id == user.id
    ).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    db.delete(address)
    db.commit()
