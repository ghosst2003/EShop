"""管理端发货地→目的地→运费规则管理"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Country, Product, ShippingOriginRule, ShippingMethod, OperationLog
from app.schemas import ShippingOriginRuleCreate, ShippingOriginRuleUpdate, ShippingOriginRuleOut

router = APIRouter()


def _build_rule_out(o: ShippingOriginRule) -> ShippingOriginRuleOut:
    origin = o.origin_country
    dest = o.destination_country
    return ShippingOriginRuleOut(
        id=o.id,
        origin_country_code=o.origin_country_code,
        origin_country_name=origin.name_en if origin else o.origin_country_code,
        origin_flag_emoji=origin.flag_emoji if origin else None,
        destination_country_code=o.destination_country_code,
        destination_country_name=dest.name_en if dest else o.destination_country_code,
        destination_flag_emoji=dest.flag_emoji if dest else None,
        shipping_method_id=o.shipping_method_id,
        shipping_method_name=o.method.name if o.method else None,
        fee=o.fee,
        is_active=o.is_active,
    )


@router.get("", response_model=list[ShippingOriginRuleOut])
def list_shipping_origin_rules(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """获取所有发货地→目的地→运费规则"""
    rules = (
        db.query(ShippingOriginRule)
        .options(
            joinedload(ShippingOriginRule.origin_country),
            joinedload(ShippingOriginRule.destination_country),
            joinedload(ShippingOriginRule.method),
        )
        .order_by(
            ShippingOriginRule.origin_country_code,
            ShippingOriginRule.destination_country_code,
        )
        .all()
    )
    return [_build_rule_out(r) for r in rules]


@router.post("", response_model=ShippingOriginRuleOut)
def create_shipping_origin_rule(
    data: ShippingOriginRuleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """新增发货地→目的地→运费规则"""
    origin = db.query(Country).filter(Country.code == data.origin_country_code.upper()).first()
    if not origin:
        raise HTTPException(status_code=400, detail=f"发货国家 '{data.origin_country_code}' 不存在")
    dest = db.query(Country).filter(Country.code == data.destination_country_code.upper()).first()
    if not dest:
        raise HTTPException(status_code=400, detail=f"目的国家 '{data.destination_country_code}' 不存在")
    method = db.query(ShippingMethod).filter(ShippingMethod.id == data.shipping_method_id).first()
    if not method:
        raise HTTPException(status_code=400, detail="派送方式不存在")

    existing = db.query(ShippingOriginRule).filter(
        ShippingOriginRule.origin_country_code == data.origin_country_code.upper(),
        ShippingOriginRule.destination_country_code == data.destination_country_code.upper(),
        ShippingOriginRule.shipping_method_id == data.shipping_method_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该发货地→目的地→派送方式的规则已存在")

    rule = ShippingOriginRule(
        origin_country_code=data.origin_country_code.upper(),
        destination_country_code=data.destination_country_code.upper(),
        shipping_method_id=data.shipping_method_id,
        fee=data.fee,
        is_active=1 if data.is_active else 0,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return _build_rule_out(rule)


@router.put("/{rule_id}", response_model=ShippingOriginRuleOut)
def update_shipping_origin_rule(
    rule_id: int,
    data: ShippingOriginRuleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """更新规则"""
    rule = db.query(ShippingOriginRule).filter(ShippingOriginRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    if data.fee is not None:
        rule.fee = data.fee
    if data.is_active is not None:
        rule.is_active = 1 if data.is_active else 0
    db.commit()
    db.refresh(rule)
    return _build_rule_out(rule)


@router.delete("/{rule_id}")
def delete_shipping_origin_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """删除规则"""
    rule = db.query(ShippingOriginRule).filter(ShippingOriginRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    db.delete(rule)
    db.commit()
    return {"message": "规则已删除"}
