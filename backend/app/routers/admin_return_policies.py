"""Admin: 退货政策管理"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, GlobalReturnPolicy, ProductReturnPolicy
from app.schemas import (
    GlobalReturnPolicyCreate,
    GlobalReturnPolicyUpdate,
    GlobalReturnPolicyOut,
    ProductReturnPolicyCreate,
    ProductReturnPolicyUpdate,
    ProductReturnPolicyOut,
    ReturnPolicyResolved,
)

router = APIRouter()


# ============================================================
# 全局退货政策
# ============================================================

@router.get("/return-policy", response_model=GlobalReturnPolicyOut)
def get_global_return_policy(
    db: Session = Depends(get_db),
):
    """获取全局默认退货政策"""
    policy = db.query(GlobalReturnPolicy).filter(GlobalReturnPolicy.is_active == 1).first()
    if not policy:
        # 如果没有，创建默认值
        policy = GlobalReturnPolicy(
            return_days=30,
            buyer_pays_return_shipping=1,
            restocking_fee_percent=0,
            description="",
            description_en="",
        )
        db.add(policy)
        db.commit()
        db.refresh(policy)
    return policy


@router.put("/return-policy", response_model=GlobalReturnPolicyOut)
def update_global_return_policy(
    data: GlobalReturnPolicyUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """更新全局退货政策"""
    policy = db.query(GlobalReturnPolicy).filter(GlobalReturnPolicy.is_active == 1).first()
    if not policy:
        policy = GlobalReturnPolicy()
        db.add(policy)
        db.commit()
        db.refresh(policy)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(policy, field, value)

    db.commit()
    db.refresh(policy)
    return policy


# ============================================================
# 商品级别退货政策覆盖
# ============================================================

@router.get("/products/{product_id}/return-policy", response_model=ProductReturnPolicyOut | None)
def get_product_return_policy(
    product_id: int,
    db: Session = Depends(get_db),
):
    """获取商品级别的退货政策覆盖"""
    return db.query(ProductReturnPolicy).filter(
        ProductReturnPolicy.product_id == product_id
    ).first()


@router.post("/products/{product_id}/return-policy", response_model=ProductReturnPolicyOut)
def set_product_return_policy(
    product_id: int,
    data: ProductReturnPolicyCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """设置商品级别退货政策覆盖（不存在则创建）"""
    existing = db.query(ProductReturnPolicy).filter(
        ProductReturnPolicy.product_id == product_id
    ).first()
    if existing:
        for field, value in data.model_dump(exclude_unset=True, exclude={"product_id"}).items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing

    policy = ProductReturnPolicy(product_id=product_id, **data.model_dump(exclude={"product_id"}))
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.delete("/products/{product_id}/return-policy")
def delete_product_return_policy(
    product_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """删除商品级别覆盖（回退到全局默认）"""
    policy = db.query(ProductReturnPolicy).filter(
        ProductReturnPolicy.product_id == product_id
    ).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Product return policy not found")
    db.delete(policy)
    db.commit()
    return {"message": "Product return policy deleted"}


# ============================================================
# 解析后的退货政策（前端买家使用）
# ============================================================

@router.get("/resolve-return-policy/{product_id}", response_model=ReturnPolicyResolved)
def resolve_return_policy(
    product_id: int,
    db: Session = Depends(get_db),
):
    """获取合并后的退货政策（商品覆盖优先，否则全局默认）"""
    global_policy = db.query(GlobalReturnPolicy).filter(
        GlobalReturnPolicy.is_active == 1
    ).first()
    if not global_policy:
        global_policy = GlobalReturnPolicy()

    product_policy = db.query(ProductReturnPolicy).filter(
        ProductReturnPolicy.product_id == product_id
    ).first()

    def get_val(field: str, fallback):
        if product_policy is None:
            return getattr(global_policy, field, fallback)
        val = getattr(product_policy, field, None)
        if val is None:
            return getattr(global_policy, field, fallback)
        return val

    return ReturnPolicyResolved(
        return_days=get_val("return_days", 30),
        buyer_pays_return_shipping=bool(get_val("buyer_pays_return_shipping", 1)),
        restocking_fee_percent=float(get_val("restocking_fee_percent", 0)),
        description=get_val("description", ""),
        description_en=get_val("description_en", ""),
    )
