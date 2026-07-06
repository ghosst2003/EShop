from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers import (
    auth,
    products_public,
    categories_public,
    products,          # was admin_products
    admin_categories,
    admin_countries,
    admin_shipping_methods,
    admin_shipping_origins,
    admin_flash_deals,
    flash_deals_public,
    admin_banners,
    banners_public,
    gdpr_public,
    admin_gdpr,
    admin_orders,
    buyer_auth,
    cart,
    buyer_orders,
    payment,
    addresses,
    shipping,         # now a package (was a flat module)
    admin_return_policies,
    admin_payment_methods,
    admin_global_shipping_settings,
    shipping_info,
)

app = FastAPI(title="ESHShop API", version="1.0.0")

# CORS — 开发阶段允许所有来源，生产环境应限制域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
app.include_router(buyer_auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(products_public.router, prefix="/api/products", tags=["Products - Public"])
app.include_router(categories_public.router, prefix="/api/categories", tags=["Categories - Public"])
app.include_router(products.router, prefix="/api/admin/products", tags=["Products - Admin"])
app.include_router(admin_categories.router, prefix="/api/admin/categories", tags=["Categories - Admin"])
app.include_router(admin_countries.router, prefix="/api/admin/countries", tags=["Countries - Admin"])
app.include_router(admin_shipping_methods.router, prefix="/api/admin/shipping-methods", tags=["Shipping Methods - Admin"])
app.include_router(admin_shipping_origins.router, prefix="/api/admin/shipping-origins", tags=["Shipping Origins - Admin"])
app.include_router(admin_flash_deals.router, prefix="/api/admin/flash-deals", tags=["Flash Deals - Admin"])
app.include_router(flash_deals_public.router, prefix="/api/flash-deals", tags=["Flash Deals - Public"])
app.include_router(admin_banners.router, prefix="/api/admin/banners", tags=["Banners - Admin"])
app.include_router(banners_public.router, prefix="/api/banners", tags=["Banners - Public"])
app.include_router(gdpr_public.router, prefix="/api/gdpr", tags=["GDPR - Public"])
app.include_router(admin_gdpr.router, prefix="/api/admin/gdpr", tags=["GDPR - Admin"])
app.include_router(admin_orders.router, prefix="/api/admin/orders", tags=["Orders - Admin"])
app.include_router(cart.router, prefix="/api/cart", tags=["Shopping Cart"])
app.include_router(buyer_orders.router, prefix="/api/orders", tags=["Orders - Buyer"])
app.include_router(payment.router, prefix="/api/payments", tags=["Payments"])
app.include_router(addresses.router, prefix="/api/addresses", tags=["Addresses"])
app.include_router(shipping.router, prefix="/api/shipping", tags=["Shipping - Public"])
app.include_router(admin_return_policies.router, prefix="/api/admin/shipping", tags=["Return Policies - Admin"])
app.include_router(admin_payment_methods.router, prefix="/api/admin/payment-methods", tags=["Payment Methods - Admin"])
app.include_router(admin_global_shipping_settings.router, prefix="/api/admin/shipping-settings", tags=["Shipping Settings - Admin"])
app.include_router(shipping_info.router, prefix="/api/shipping-info", tags=["Shipping Info - Public"])


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


# 挂载上传文件目录
uploads_dir = Path(__file__).parent.parent / "uploads"
if uploads_dir.exists():
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# 挂载管理端前端 (开发阶段可选)
admin_dir = Path(__file__).parent.parent / "static" / "admin"
buyer_dir = Path(__file__).parent.parent / "static" / "buyer"

if admin_dir.exists():
    # 管理端静态资源
    admin_assets_dir = admin_dir / "assets"
    if admin_assets_dir.exists():
        app.mount("/admin/assets", StaticFiles(directory=admin_assets_dir), name="admin-assets")

    @app.get("/admin/{full_path:path}")
    async def serve_admin_spa(full_path: str):
        index_file = admin_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Not Found")

if buyer_dir.exists():
    # 挂载静态资源目录
    assets_dir = buyer_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="buyer-assets")

    # SPA catch-all: 非 API、非静态资源请求都返回 index.html
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # 排除 API 和 uploads 路径
        if full_path.startswith("api/") or full_path.startswith("uploads/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not Found")
        index_file = buyer_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Not Found")
