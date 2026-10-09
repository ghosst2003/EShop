from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session, joinedload

from app.models import (
    ProductShippingOverride,
    ShippingMethod,
    ShippingMethodCountry,
    ShippingOriginRule,
)


MONEY = Decimal("0.01")


@dataclass(frozen=True)
class CartShippingQuote:
    method: str
    total: Decimal
    items: list[dict]
    configured: bool


def money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(MONEY, rounding=ROUND_HALF_UP)


def _method_country_cost(weight_kg: Decimal, method_country, override=None) -> Decimal:
    min_weight = Decimal(str(method_country.min_weight_kg or 0.5))
    billable_weight = max(weight_kg, min_weight)
    if override and not override.is_disabled and override.override_base_fee is not None:
        base_fee = Decimal(str(override.override_base_fee))
        per_kg = Decimal(str(override.override_per_kg_fee or 0))
        surcharge = Decimal(str(override.surcharge or 0))
    else:
        base_fee = Decimal(str(method_country.base_fee or 0))
        per_kg = Decimal(str(method_country.per_kg_fee or 0))
        surcharge = Decimal("0")
    return money(max(Decimal("0"), base_fee + max(Decimal("0"), billable_weight - min_weight) * per_kg + surcharge))


def quote_cart_shipping(db: Session, cart_items, country_code: str) -> CartShippingQuote:
    """Return an authoritative, server-side quote for the exact cart rows."""
    country_code = (country_code or "").strip().upper()
    total = Decimal("0")
    item_quotes = []
    method_names = []
    configured_count = 0

    for cart_item in cart_items:
        product = cart_item.product
        item_cost = Decimal("0")
        method_name = "Standard delivery"
        configured = False

        if product.origin_country_code:
            rule = (
                db.query(ShippingOriginRule)
                .join(ShippingMethod)
                .options(joinedload(ShippingOriginRule.method))
                .filter(
                    ShippingOriginRule.origin_country_code == product.origin_country_code,
                    ShippingOriginRule.destination_country_code == country_code,
                    ShippingOriginRule.is_active == 1,
                    ShippingMethod.is_active == 1,
                )
                .order_by(ShippingOriginRule.fee.asc())
                .first()
            )
            if rule:
                override = db.query(ProductShippingOverride).filter(
                    ProductShippingOverride.product_id == product.id,
                    ProductShippingOverride.country_code == country_code,
                    ProductShippingOverride.shipping_method_id == rule.shipping_method_id,
                ).first()
                if not (override and override.is_disabled):
                    per_item = Decimal(str(rule.fee or 0))
                    if override and override.override_base_fee is not None:
                        per_item = Decimal(str(override.override_base_fee)) + Decimal(str(override.surcharge or 0))
                    item_cost = money(per_item * cart_item.quantity)
                    method_name = rule.method.name
                    configured = True

        if not configured:
            method_country = (
                db.query(ShippingMethodCountry)
                .join(ShippingMethod)
                .options(joinedload(ShippingMethodCountry.method))
                .filter(
                    ShippingMethodCountry.country_code == country_code,
                    ShippingMethod.is_active == 1,
                )
                .order_by(ShippingMethodCountry.is_default.desc(), ShippingMethodCountry.base_fee.asc())
                .first()
            )
            if method_country:
                override = db.query(ProductShippingOverride).filter(
                    ProductShippingOverride.product_id == product.id,
                    ProductShippingOverride.country_code == country_code,
                    ProductShippingOverride.shipping_method_id == method_country.shipping_method_id,
                ).first()
                if not (override and override.is_disabled):
                    weight = Decimal(str(product.weight_kg or 0.5)) * cart_item.quantity
                    item_cost = _method_country_cost(weight, method_country, override)
                    method_name = method_country.method.name
                    configured = True

        if configured:
            configured_count += 1
        method_names.append(method_name)
        total += item_cost
        item_quotes.append({
            "product_title": product.title_en or product.title,
            "quantity": cart_item.quantity,
            "shipping_cost": money(item_cost),
            "configured": configured,
        })

    unique_methods = list(dict.fromkeys(method_names))
    method = unique_methods[0] if len(unique_methods) == 1 else "Combined delivery"
    return CartShippingQuote(
        method=method,
        total=money(total),
        items=item_quotes,
        configured=configured_count == len(cart_items),
    )
