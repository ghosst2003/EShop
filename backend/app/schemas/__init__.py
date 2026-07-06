# schemas package — re-exports for backward compatibility.
# All existing imports like `from app.schemas import ProductOut` still work.

from app.schemas.auth import (
    LoginRequest,
    UserRegister,
    UserProfileUpdate,
    TokenResponse,
    UserOut,
)

from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryOut,
    CategoryTree,
)

from app.schemas.country import (
    CountryCreate,
    CountryUpdate,
    CountryOut,
)

from app.schemas.product import (
    ShippingRuleCreate,
    ShippingRuleOut,
    ProductImageOut,
    ProductCreate,
    ProductUpdate,
    ProductOut,
    ProductListResponse,
    ProductStatusUpdate,
)

from app.schemas.shipping import (
    ShippingMethodCountryCreate,
    ShippingMethodCountryOut,
    ShippingMethodCreate,
    ShippingMethodUpdate,
    ShippingMethodOut,
    ProductShippingOverrideCreate,
    ProductShippingOverrideOut,
    ShippingOriginRuleCreate,
    ShippingOriginRuleUpdate,
    ShippingOriginRuleOut,
    ProductShippingNoteCreate,
    ProductShippingNoteOut,
    ShippingCalculationRequest,
    ShippingOptionResult,
    CartShippingEstimate,
)

from app.schemas.order import (
    OrderItemCreate,
    OrderCreate,
    OrderUpdate,
    OrderStatusUpdate,
    OrderItemOut,
    OrderStatusLogOut,
    OrderOut,
    OrderListResponse,
    OrderStats,
)

from app.schemas.cart import (
    CartItemCreate,
    CartItemUpdate,
    CartItemOut,
    CartOut,
)

from app.schemas.address import (
    AddressCreate,
    AddressUpdate,
    AddressOut,
)

from app.schemas.buyer import (
    BuyerOrderCreate,
    BuyerOrderOut,
    BuyerOrderListResponse,
)

from app.schemas.payment import (
    CheckoutSessionCreate,
    CheckoutSessionResponse,
    ShippingOptionOut,
)

from app.schemas.gdpr import (
    GdprConsentRequest,
    GdprDataRequest,
    GdprRequestOut,
    GdprRequestStatusUpdate,
)

from app.schemas.log import (
    OperationLogOut,
)

from app.schemas.flash_deal import (
    FlashDealCreate,
    FlashDealUpdate,
    FlashDealProductBrief,
    FlashDealOut,
)

from app.schemas.banner import (
    BannerCreate,
    BannerUpdate,
    BannerOut,
)

from app.schemas.return_policy import (
    GlobalReturnPolicyCreate,
    GlobalReturnPolicyUpdate,
    GlobalReturnPolicyOut,
    ProductReturnPolicyCreate,
    ProductReturnPolicyUpdate,
    ProductReturnPolicyOut,
    ReturnPolicyResolved,
)

from app.schemas.payment_method import (
    PaymentMethodCreate,
    PaymentMethodUpdate,
    PaymentMethodOut,
)

from app.schemas.shipping_settings import (
    GlobalShippingSettingsCreate,
    GlobalShippingSettingsUpdate,
    GlobalShippingSettingsOut,
)

__all__ = [
    # auth
    "LoginRequest", "UserRegister", "UserProfileUpdate",
    "TokenResponse", "UserOut",
    # category
    "CategoryCreate", "CategoryUpdate", "CategoryOut", "CategoryTree",
    # country
    "CountryCreate", "CountryUpdate", "CountryOut",
    # product
    "ShippingRuleCreate", "ShippingRuleOut",
    "ProductImageOut", "ProductCreate", "ProductUpdate", "ProductOut",
    "ProductListResponse", "ProductStatusUpdate",
    # shipping
    "ShippingMethodCountryCreate", "ShippingMethodCountryOut",
    "ShippingMethodCreate", "ShippingMethodUpdate", "ShippingMethodOut",
    "ProductShippingOverrideCreate", "ProductShippingOverrideOut",
    "ShippingOriginRuleCreate", "ShippingOriginRuleUpdate", "ShippingOriginRuleOut",
    "ProductShippingNoteCreate", "ProductShippingNoteOut",
    "ShippingCalculationRequest", "ShippingOptionResult", "CartShippingEstimate",
    # order
    "OrderItemCreate", "OrderCreate", "OrderUpdate", "OrderStatusUpdate",
    "OrderItemOut", "OrderStatusLogOut", "OrderOut",
    "OrderListResponse", "OrderStats",
    # cart
    "CartItemCreate", "CartItemUpdate", "CartItemOut", "CartOut",
    # address
    "AddressCreate", "AddressUpdate", "AddressOut",
    # buyer
    "BuyerOrderCreate", "BuyerOrderOut", "BuyerOrderListResponse",
    # payment
    "CheckoutSessionCreate", "CheckoutSessionResponse", "ShippingOptionOut",
    # gdpr
    "GdprConsentRequest", "GdprDataRequest",
    "GdprRequestOut", "GdprRequestStatusUpdate",
    # log
    "OperationLogOut",
    # flash_deal
    "FlashDealCreate", "FlashDealUpdate",
    "FlashDealProductBrief", "FlashDealOut",
    # banner
    "BannerCreate", "BannerUpdate", "BannerOut",
    # return_policy
    "GlobalReturnPolicyCreate", "GlobalReturnPolicyUpdate", "GlobalReturnPolicyOut",
    "ProductReturnPolicyCreate", "ProductReturnPolicyUpdate", "ProductReturnPolicyOut",
    "ReturnPolicyResolved",
    # payment_method
    "PaymentMethodCreate", "PaymentMethodUpdate", "PaymentMethodOut",
    # shipping_settings
    "GlobalShippingSettingsCreate", "GlobalShippingSettingsUpdate",
    "GlobalShippingSettingsOut",
]
