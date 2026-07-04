#!/usr/bin/env python3
"""
数据库迁移脚本：添加 6 项核心功能所需的新表和字段。
用法: cd backend && python migrate_db.py
"""
from sqlalchemy import create_engine, text, inspect
from app.config import settings
from app.models import Base
from app.utils import generate_slug, ensure_unique_slug


def column_exists(conn, table: str, column: str) -> bool:
    """检查列是否存在"""
    result = conn.execute(text(
        "SELECT COUNT(*) FROM information_schema.columns "
        "WHERE table_schema = DATABASE() "
        f"AND table_name = '{table}' AND column_name = '{column}'"
    )).scalar()
    return result > 0


def index_exists(conn, table: str, index: str) -> bool:
    """检查索引是否存在"""
    result = conn.execute(text(
        "SELECT COUNT(*) FROM information_schema.statistics "
        f"WHERE table_schema = DATABASE() AND table_name = '{table}' AND index_name = '{index}'"
    )).scalar()
    return result > 0


def run_migration():
    engine = create_engine(settings.database_url)

    with engine.connect() as conn:
        # 1. 更新 users 表
        print("更新 users 表...")
        conn.execute(text(
            "ALTER TABLE users MODIFY COLUMN role "
            "ENUM('admin', 'buyer') NOT NULL DEFAULT 'admin'"
        ))
        if not column_exists(conn, "users", "phone"):
            conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(50) NULL"))
        if not column_exists(conn, "users", "avatar"):
            conn.execute(text("ALTER TABLE users ADD COLUMN avatar VARCHAR(500) NULL"))

        # 2. 更新 products 表
        print("更新 products 表...")
        if not column_exists(conn, "products", "stock_quantity"):
            conn.execute(text("ALTER TABLE products ADD COLUMN stock_quantity INT NOT NULL DEFAULT 0"))
        if not column_exists(conn, "products", "auto_manage_stock"):
            conn.execute(text("ALTER TABLE products ADD COLUMN auto_manage_stock TINYINT(1) NOT NULL DEFAULT 1"))
        if not column_exists(conn, "products", "slug"):
            # 先加列，允许 NULL
            conn.execute(text("ALTER TABLE products ADD COLUMN slug VARCHAR(255) NULL"))

        # 为还没有 slug 的商品生成 slug（包括空字符串的情况）
        products = conn.execute(text(
            "SELECT id, title, title_en FROM products WHERE slug IS NULL OR slug = ''"
        )).fetchall()
        if products:
            existing = set()
            for pid, title, title_en in products:
                base = generate_slug(title_en or title)
                slug = ensure_unique_slug(base, existing)
                existing.add(slug)
                conn.execute(text(
                    "UPDATE products SET slug = :slug WHERE id = :pid"
                ), {"slug": slug, "pid": pid})
            conn.commit()
            print(f"  为 {len(products)} 个商品生成 slug")

        # 确保 slug 为 NOT NULL
        conn.execute(text("ALTER TABLE products MODIFY COLUMN slug VARCHAR(255) NOT NULL"))
        if not index_exists(conn, "products", "ix_products_slug"):
            conn.execute(text("ALTER TABLE products ADD UNIQUE INDEX ix_products_slug (slug)"))
        if not column_exists(conn, "products", "origin_country_code"):
            conn.execute(text("ALTER TABLE products ADD COLUMN origin_country_code VARCHAR(10) NULL"))
        if not index_exists(conn, "products", "idx_products_origin_country"):
            conn.execute(text("ALTER TABLE products ADD INDEX idx_products_origin_country (origin_country_code)"))

        # 3. 更新 orders 表
        print("更新 orders 表...")
        if not column_exists(conn, "orders", "buyer_id"):
            conn.execute(text("ALTER TABLE orders ADD COLUMN buyer_id INT NULL"))
        if not index_exists(conn, "orders", "idx_orders_buyer_id"):
            conn.execute(text("ALTER TABLE orders ADD INDEX idx_orders_buyer_id (buyer_id)"))
        if not column_exists(conn, "orders", "payment_intent_id"):
            conn.execute(text("ALTER TABLE orders ADD COLUMN payment_intent_id VARCHAR(255) NULL"))
        if not column_exists(conn, "orders", "payment_status"):
            conn.execute(text(
                "ALTER TABLE orders ADD COLUMN payment_status "
                "ENUM('pending', 'requires_action', 'paid', 'failed', 'refunded') "
                "DEFAULT 'pending' NOT NULL"
            ))
        if not column_exists(conn, "orders", "shipping_price"):
            conn.execute(text("ALTER TABLE orders ADD COLUMN shipping_price DECIMAL(10,2) NULL"))
        if not column_exists(conn, "orders", "shipping_country"):
            conn.execute(text("ALTER TABLE orders ADD COLUMN shipping_country VARCHAR(10) NULL"))

        conn.commit()

    # 4. 创建新表
    print("创建新表 (carts, cart_items, addresses, product_shipping_rules, countries, flash_deals)...")
    Base.metadata.create_all(bind=engine)

    # 5. 初始化国家数据
    print("初始化国家数据...")
    default_countries = [
        ('CN', '中国', 'China', '🇳', 0),
        ('DE', '德国', 'Germany', '🇩🇪', 1),
        ('FR', '法国', 'France', '🇫🇷', 2),
        ('IT', '意大利', 'Italy', '🇮🇹', 3),
        ('ES', '西班牙', 'Spain', '🇪🇸', 4),
        ('NL', '荷兰', 'Netherlands', '🇱', 5),
        ('BE', '比利时', 'Belgium', '🇧🇪', 6),
        ('AT', '奥地利', 'Austria', '🇦🇹', 7),
        ('PL', '波兰', 'Poland', '🇵🇱', 8),
        ('PT', '葡萄牙', 'Portugal', '🇵🇹', 9),
    ]
    with engine.connect() as conn:
        for code, name, name_en, flag, sort_order in default_countries:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM countries WHERE code = :code"
            ), {"code": code}).scalar()
            if result == 0:
                conn.execute(text(
                    "INSERT INTO countries (code, name, name_en, flag_emoji, is_active, sort_order) "
                    "VALUES (:code, :name, :name_en, :flag, 1, :sort_order)"
                ), {"code": code, "name": name, "name_en": name_en, "flag": flag, "sort_order": sort_order})
        conn.commit()

    print("✅ 迁移完成！")

    # 6. 确保新表的 country_code 列 collation 对齐
    print("对齐 shipping_origin_rules 表 collation...")
    with engine.connect() as conn:
        try:
            conn.execute(text(
                "ALTER TABLE shipping_origin_rules "
                "MODIFY COLUMN origin_country_code VARCHAR(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL"
            ))
            conn.execute(text(
                "ALTER TABLE shipping_origin_rules "
                "MODIFY COLUMN destination_country_code VARCHAR(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL"
            ))
            conn.commit()
        except Exception as e:
            print(f"  collation 对齐跳过: {e}")

    print("✅ 全部完成！")


if __name__ == "__main__":
    run_migration()
