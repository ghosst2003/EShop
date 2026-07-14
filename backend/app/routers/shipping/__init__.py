"""Public: 派送费用计算接口"""
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import (
    Product, ShippingMethod, ShippingMethodCountry, ProductShippingOverride,
    Country, Cart, CartItem, User, ShippingOriginRule,
)
from app.schemas import (
    ShippingOptionResult, ShippingCalculationRequest, CartShippingEstimate,
)

router = APIRouter()


def _calculate_shipping_cost(
    weight_kg: Decimal,
    method_country: ShippingMethodCountry,
    override: Optional[ProductShippingOverride] = None,
) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    """
    计算单个商品的运费
    返回: (base_fee, weight_fee, surcharge, total)
    """
    min_weight = Decimal(str(method_country.min_weight_kg or 0.5))
    billable_weight = max(weight_kg, min_weight)

    if override and not override.is_disabled and override.override_base_fee is not None:
        base_fee = Decimal(str(override.override_base_fee))
        per_kg = Decimal(str(override.override_per_kg_fee or 0))
        surcharge = Decimal(str(override.surcharge or 0))
    else:
        base_fee = Decimal(str(method_country.base_fee))
        per_kg = Decimal(str(method_country.per_kg_fee or 0))
        surcharge = Decimal("0")

    excess = max(Decimal("0"), billable_weight - min_weight)
    weight_fee = excess * per_kg
    total = base_fee + weight_fee + surcharge

    return base_fee, weight_fee, surcharge, max(total, Decimal("0"))


@router.post("/calculate", response_model=list[ShippingOptionResult])
def calculate_shipping(
    data: ShippingCalculationRequest,
    db: Session = Depends(get_db),
):
    """计算单个商品发往指定国家的运费选项

    优先使用 ShippingOriginRule（发货地→目的地→派送方式→固定运费）
    回退到 ShippingMethodCountry（基础运费 + 重量计价）
    """
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    country_code = data.destination_country.upper()
    weight = Decimal(str(product.weight_kg or 0.5)) * data.quantity
    origin_code = product.origin_country_code  # 可能为 None

    results = []

    # 优先方案：使用 ShippingOriginRule（发货地→目的地→固定运费）
    if origin_code:
        origin_rules = (
            db.query(ShippingOriginRule)
            .join(ShippingMethod)
            .filter(
                ShippingOriginRule.origin_country_code == origin_code,
                ShippingOriginRule.destination_country_code == country_code,
                ShippingOriginRule.is_active == 1,
                ShippingMethod.is_active == 1,
            )
            .options(joinedload(ShippingOriginRule.method))
            .all()
        )

        for rule in origin_rules:
            # 检查是否有商品级别禁用
            override = db.query(ProductShippingOverride).filter(
                ProductShippingOverride.product_id == product.id,
                ProductShippingOverride.country_code == country_code,
                ProductShippingOverride.shipping_method_id == rule.shipping_method_id,
            ).first()

            if override and override.is_disabled:
                continue

            total = Decimal(str(rule.fee))
            if override and override.override_base_fee is not None:
                total = Decimal(str(override.override_base_fee)) + Decimal(str(override.surcharge or 0))

            results.append(ShippingOptionResult(
                shipping_method_id=rule.shipping_method_id,
                shipping_method=rule.method.name,
                base_fee=Decimal(str(rule.fee)),
                per_kg_fee=Decimal("0"),
                weight_fee=Decimal("0"),
                surcharge=override.surcharge if override else Decimal("0"),
                total_fee=max(total, Decimal("0")),
                estimated_days_min=None,
                estimated_days_max=None,
                is_default=False,
                is_override=bool(override and override.override_base_fee is not None),
            ))

    # 如果没找到 origin rules，回退到 ShippingMethodCountry 计算
    if not results:
        method_countries = (
            db.query(ShippingMethodCountry)
            .join(ShippingMethod)
            .filter(
                ShippingMethodCountry.country_code == country_code,
                ShippingMethod.is_active == 1,
            )
            .options(joinedload(ShippingMethodCountry.method))
            .all()
        )

        if not method_countries:
            method_countries = (
                db.query(ShippingMethodCountry)
                .join(ShippingMethod)
                .filter(
                    ShippingMethod.is_active == 1,
                    ShippingMethodCountry.is_default == 1,
                )
                .options(joinedload(ShippingMethodCountry.method))
                .all()
            )

        for mc in method_countries:
            override = db.query(ProductShippingOverride).filter(
                ProductShippingOverride.product_id == product.id,
                ProductShippingOverride.country_code == country_code,
                ProductShippingOverride.shipping_method_id == mc.shipping_method_id,
            ).first()

            if override and override.is_disabled:
                continue

            base_fee, weight_fee, surcharge, total = _calculate_shipping_cost(weight, mc, override)

            results.append(ShippingOptionResult(
                shipping_method_id=mc.shipping_method_id,
                shipping_method=mc.method.name,
                base_fee=base_fee,
                per_kg_fee=Decimal(str(mc.per_kg_fee)),
                weight_fee=weight_fee,
                surcharge=surcharge,
                total_fee=total,
                estimated_days_min=mc.estimated_days_min,
                estimated_days_max=mc.estimated_days_max,
                is_default=bool(mc.is_default),
                is_override=bool(override and override.override_base_fee is not None),
            ))

    # 排序：默认优先，其次按总价
    results.sort(key=lambda r: (not r.is_default, r.total_fee))
    return results


@router.get("/products/{slug}/shipping-table")
def get_product_shipping_table(
    slug: str,
    db: Session = Depends(get_db),
):
    """
    获取商品在所有支持国家的运费表格
    优先使用 ShippingOriginRule，回退到 ShippingMethodCountry
    返回: [{country_code, country_name, flag_emoji, options: [{method, price, days}]}]
    """
    product = db.query(Product).filter(Product.slug == slug, Product.status == "active").first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    weight = Decimal(str(product.weight_kg or 0.5))
    origin_code = product.origin_country_code

    country_data = {}

    # 优先：使用 ShippingOriginRule
    if origin_code:
        rules = (
            db.query(ShippingOriginRule, Country)
            .join(ShippingMethod)
            .outerjoin(Country, ShippingOriginRule.destination_country_code == Country.code)
            .filter(
                ShippingOriginRule.origin_country_code == origin_code,
                ShippingOriginRule.is_active == 1,
                ShippingMethod.is_active == 1,
            )
            .order_by(Country.sort_order, Country.name)
            .all()
        )

        for rule, country in rules:
            cc = rule.destination_country_code
            if cc not in country_data:
                country_data[cc] = {
                    "country_code": cc,
                    "country_name": country.name_en if country else cc,
                    "flag_emoji": country.flag_emoji if country else "",
                    "options": [],
                }

            # 检查商品级别覆盖
            override = db.query(ProductShippingOverride).filter(
                ProductShippingOverride.product_id == product.id,
                ProductShippingOverride.country_code == cc,
                ProductShippingOverride.shipping_method_id == rule.shipping_method_id,
            ).first()

            if override and override.is_disabled:
                continue

            total = Decimal(str(rule.fee))
            if override and override.override_base_fee is not None:
                total = Decimal(str(override.override_base_fee)) + Decimal(str(override.surcharge or 0))

            country_data[cc]["options"].append({
                "shipping_method": rule.method.name if rule.method else "",
                "total_fee": str(max(total, Decimal("0"))),
                "estimated_days_min": None,
                "estimated_days_max": None,
                "is_default": False,
            })

    # 回退：ShippingMethodCountry（当没有 origin rules 时）
    if not country_data:
        mc_query = (
            db.query(ShippingMethodCountry, Country)
            .join(ShippingMethod, ShippingMethodCountry.shipping_method_id == ShippingMethod.id)
            .outerjoin(Country, ShippingMethodCountry.country_code == Country.code)
            .filter(ShippingMethod.is_active == 1)
            .order_by(Country.sort_order, Country.name)
            .all()
        )

        for mc, country in mc_query:
            cc = mc.country_code
            if cc not in country_data:
                country_data[cc] = {
                    "country_code": cc,
                    "country_name": country.name_en if country else cc,
                    "flag_emoji": country.flag_emoji if country else "",
                    "options": [],
                }

            override = db.query(ProductShippingOverride).filter(
                ProductShippingOverride.product_id == product.id,
                ProductShippingOverride.country_code == cc,
                ProductShippingOverride.shipping_method_id == mc.shipping_method_id,
            ).first()

            if override and override.is_disabled:
                continue

            _, _, _, total = _calculate_shipping_cost(weight, mc, override)
            country_data[cc]["options"].append({
                "shipping_method": mc.method.name,
                "total_fee": str(total),
                "estimated_days_min": mc.estimated_days_min,
                "estimated_days_max": mc.estimated_days_max,
                "is_default": bool(mc.is_default),
            })

    # 过滤掉没有任何选项的国家
    result = [v for v in country_data.values() if v["options"]]
    result.sort(key=lambda x: x["country_name"])
    return result


@router.get("/cart/shipping-estimate", response_model=CartShippingEstimate)
def get_cart_shipping_estimate(
    country: str = Query(..., description="Destination country code"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    计算整个购物车发往指定国家的运费
    返回每项商品的运费和总计
    """
    cart = db.query(Cart).options(
        joinedload(Cart.items).joinedload(CartItem.product)
    ).filter(Cart.buyer_id == user.id).first()

    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    country_code = country.upper()
    subtotal = Decimal("0")
    shipping_total = Decimal("0")
    items_result = []

    for ci in cart.items:
        product = ci.product
        if not product:
            continue
        subtotal += Decimal(str(product.sale_price)) * ci.quantity

        origin_code = product.origin_country_code
        total = Decimal("0")

        # 优先：使用 ShippingOriginRule
        if origin_code:
            rule = (
                db.query(ShippingOriginRule)
                .join(ShippingMethod)
                .filter(
                    ShippingOriginRule.origin_country_code == origin_code,
                    ShippingOriginRule.destination_country_code == country_code,
                    ShippingOriginRule.is_active == 1,
                    ShippingMethod.is_active == 1,
                )
                .order_by(ShippingOriginRule.fee)
                .first()
            )
            if rule:
                total = Decimal(str(rule.fee)) * ci.quantity

        # 回退：ShippingMethodCountry
        if not total:
            method_countries = (
                db.query(ShippingMethodCountry)
                .join(ShippingMethod)
                .filter(
                    ShippingMethodCountry.country_code == country_code,
                    ShippingMethod.is_active == 1,
                )
                .options(joinedload(ShippingMethodCountry.method))
                .order_by(ShippingMethodCountry.is_default.desc(), ShippingMethodCountry.base_fee)
                .limit(1)
                .all()
            )

            if method_countries:
                mc = method_countries[0]
                weight = Decimal(str(product.weight_kg or 0.5)) * ci.quantity
                _, _, _, total = _calculate_shipping_cost(weight, mc)

        shipping_total += total
        items_result.append({
            "product_title": product.title_en or product.title,
            "quantity": ci.quantity,
            "shipping_cost": str(total),
        })

    return CartShippingEstimate(
        country_code=country_code,
        items=items_result,
        shipping_total=shipping_total,
        grand_total=subtotal + shipping_total,
    )


@router.get("/countries")
def list_active_countries(
    db: Session = Depends(get_db),
):
    """获取所有启用的国家列表（公开接口）"""
    countries = db.query(Country).filter(Country.is_active == 1).order_by(Country.sort_order, Country.name).all()
    return [
        {
            "code": c.code,
            "name": c.name,
            "name_en": c.name_en,
            "flag_emoji": c.flag_emoji,
            "pickup_enabled": bool(c.pickup_enabled),
        }
        for c in countries
    ]
