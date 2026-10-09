from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings

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
    admin_promo_items,
    promo_items_public,
    commerce,
)

is_production = settings.environment.lower() == "production"
app = FastAPI(
    title="BeCool API",
    version="1.0.0",
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json",
)

# CORS origins are explicit in every environment and configurable per deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response

# User-Agent 检测：移动端自动跳转到手机端
@app.middleware("http")
async def mobile_redirect(request: Request, call_next):
    # 如果带 ?desktop=1 参数，不跳转
    if "desktop" in request.query_params:
        return await call_next(request)

    path = request.url.path
    # 只处理根路径和买家端路径，排除管理端和 API
    if path in ("/", "/index.html") or (path.startswith("/assets/") and not path.startswith("/admin")):
        ua = request.headers.get("user-agent", "").lower()
        mobile_agents = ["mobile", "android", "iphone", "ipad", "ipod", "blackberry", "windows phone"]
        if any(agent in ua for agent in mobile_agents):
            if path == "/" or path == "/index.html":
                return RedirectResponse(url="/mobile/")
            # /assets/... → /mobile/assets/...
            if path.startswith("/assets/"):
                return RedirectResponse(url=f"/mobile/{path}")
    return await call_next(request)

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
app.include_router(admin_promo_items.router, prefix="/api/admin/promo-items", tags=["Promo Items - Admin"])
app.include_router(promo_items_public.router, prefix="/api/promo-items", tags=["Promo Items - Public"])
app.include_router(commerce.router, prefix="/api", tags=["Saved Products & Reviews"])


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
        # 排除 API、uploads 和 mobile 路径
        if full_path.startswith("api/") or full_path.startswith("uploads/") or full_path.startswith("mobile/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not Found")
        index_file = buyer_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Not Found")

# 手机端前端静态文件
mobile_dir = Path(__file__).parent.parent / "static" / "mobile"
if mobile_dir.exists():
    mobile_assets_dir = mobile_dir / "assets"
    if mobile_assets_dir.exists():
        app.mount("/mobile/assets", StaticFiles(directory=mobile_assets_dir), name="mobile-assets")

    @app.get("/mobile/{full_path:path}")
    async def serve_mobile_spa(full_path: str):
        index_file = mobile_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Not Found")
elif not buyer_dir.exists():
    # 如果两个前端都没构建，只返回 API 健康状态
    pass
