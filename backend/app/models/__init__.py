from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models so Base.metadata knows about them
from app.models.user import User
from app.models.category import Category
from app.models.country import Country
from app.models.product import Product, ProductImage, ProductShippingRule
from app.models.order import Order, OrderItem, OrderStatusLog
from app.models.cart import Cart, CartItem
from app.models.address import Address
from app.models.shipping import (
    ShippingMethod,
    ShippingMethodCountry,
    ProductShippingOverride,
    ProductShippingNote,
    ShippingOriginRule,
)
from app.models.gdpr import GdprConsentLog, DataDeletionRequest
from app.models.log import OperationLog
from app.models.flash_deal import FlashDeal
from app.models.banner import Banner
from app.models.return_policy import GlobalReturnPolicy, ProductReturnPolicy
from app.models.payment_method import PaymentMethod
from app.models.shipping_settings import GlobalShippingSettings

# Create tables
from app.database import engine
Base.metadata.create_all(bind=engine)
