"""购物车路由 — 买家管理购物车"""
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Cart, CartItem, Product
from app.schemas import CartItemCreate, CartItemUpdate, CartOut, CartItemOut

router = APIRouter()


def get_or_create_cart(user: User, db: Session) -> Cart:
    """获取或创建用户的购物车"""
    cart = db.query(Cart).filter(Cart.buyer_id == user.id).first()
    if not cart:
        cart = Cart(buyer_id=user.id)
        db.add(cart)
        db.flush()
    return cart


def compute_cart(cart: Cart) -> CartOut:
    """计算购物车总额和商品数"""
    total_items = 0
    subtotal = Decimal("0")
    items_out = []

    for ci in cart.items:
        product = ci.product
        if product and product.status == "active":
            total_items += ci.quantity
            subtotal += Decimal(str(product.sale_price)) * ci.quantity
            items_out.append(CartItemOut(
                id=ci.id,
                product_id=ci.product_id,
                quantity=ci.quantity,
                product=ci.product,
            ))

    return CartOut(
        id=cart.id,
        buyer_id=cart.buyer_id,
        items=items_out,
        total_items=total_items,
        subtotal=subtotal,
    )


@router.get("", response_model=CartOut)
def get_cart(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的购物车"""
    if user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers have carts")

    cart = get_or_create_cart(user, db)
    db.refresh(cart)
    for item in cart.items:
        db.refresh(item)
        if item.product:
            db.refresh(item.product)

    db.commit()  # 创建 cart 后 commit
    # 重新查询以加载关联
    cart = db.query(Cart).options(
        joinedload(Cart.items).joinedload(CartItem.product)
    ).filter(Cart.buyer_id == user.id).first()

    return compute_cart(cart)


@router.post("/items", response_model=CartItemOut, status_code=201)
def add_to_cart(
    data: CartItemCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """添加商品到购物车"""
    if user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can add to cart")

    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.status != "active":
        raise HTTPException(status_code=400, detail="Product is not available")
    if product.auto_manage_stock and product.stock_quantity < data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    cart = get_or_create_cart(user, db)

    # 检查是否已存在该商品
    existing = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == data.product_id,
    ).first()

    if existing:
        new_qty = existing.quantity + data.quantity
        if product.auto_manage_stock and product.stock_quantity < new_qty:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        existing.quantity = new_qty
        item = existing
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=data.product_id,
            quantity=data.quantity,
        )
        db.add(item)

    db.commit()
    db.refresh(item)
    db.refresh(item.product)

    return CartItemOut(id=item.id, product_id=item.product_id, quantity=item.quantity, product=item.product)


@router.put("/items/{item_id}", response_model=CartItemOut)
def update_cart_item(
    item_id: int,
    data: CartItemUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新购物车商品数量"""
    if user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can update cart")

    cart = get_or_create_cart(user, db)
    item = db.query(CartItem).filter(
        CartItem.id == item_id, CartItem.cart_id == cart.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if data.quantity <= 0:
        db.delete(item)
        db.commit()
        return CartItemOut(id=item.id, product_id=item.product_id, quantity=0)

    product = db.query(Product).filter(Product.id == item.product_id).first()
    if product and product.auto_manage_stock and product.stock_quantity < data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    item.quantity = data.quantity
    db.commit()
    db.refresh(item)
    if item.product:
        db.refresh(item.product)

    return CartItemOut(id=item.id, product_id=item.product_id, quantity=item.quantity, product=item.product)


@router.delete("/items/{item_id}", status_code=204)
def remove_from_cart(
    item_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """从购物车中移除商品"""
    if user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can remove from cart")

    cart = get_or_create_cart(user, db)
    item = db.query(CartItem).filter(
        CartItem.id == item_id, CartItem.cart_id == cart.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(item)
    db.commit()


@router.delete("/clear", status_code=204)
def clear_cart(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """清空购物车"""
    if user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can clear cart")

    cart = get_or_create_cart(user, db)
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
