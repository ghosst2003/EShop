"""
Migration: Add global shipping method system
- Create shipping_methods, shipping_method_countries, product_shipping_overrides tables
- Add weight/size columns to products table
- Migrate existing product_shipping_rules data into the new structure
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.database import engine


def migrate():
    with engine.connect() as conn:
        dialect = engine.dialect.name

        if dialect == "mysql":
            _run_mysql_migration(conn)
        else:
            _run_sqlite_migration(conn)

        conn.commit()
    print("Migration completed successfully.")


def _run_mysql_migration(conn):
    """MySQL migration"""
    # 1. Create shipping_methods table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS shipping_methods (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(50) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            name_en VARCHAR(100) NOT NULL,
            description TEXT,
            is_active TINYINT(1) NOT NULL DEFAULT 1,
            sort_order INT NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """))

    # 2. Create shipping_method_countries table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS shipping_method_countries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            shipping_method_id INT NOT NULL,
            country_code VARCHAR(10) NOT NULL,
            base_fee DECIMAL(10,2) NOT NULL,
            per_kg_fee DECIMAL(10,2) NOT NULL DEFAULT 0,
            min_weight_kg DECIMAL(10,2) DEFAULT 0.5,
            max_weight_kg DECIMAL(10,2),
            estimated_days_min INT,
            estimated_days_max INT,
            is_default TINYINT(1) NOT NULL DEFAULT 0,
            FOREIGN KEY (shipping_method_id) REFERENCES shipping_methods(id) ON DELETE CASCADE,
            UNIQUE KEY unique_method_country (shipping_method_id, country_code),
            INDEX idx_country (country_code)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """))

    # 3. Create product_shipping_overrides table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS product_shipping_overrides (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            country_code VARCHAR(10) NOT NULL,
            shipping_method_id INT NOT NULL,
            override_base_fee DECIMAL(10,2),
            override_per_kg_fee DECIMAL(10,2),
            surcharge DECIMAL(10,2) DEFAULT 0,
            is_disabled TINYINT(1) NOT NULL DEFAULT 0,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (shipping_method_id) REFERENCES shipping_methods(id),
            UNIQUE KEY unique_product_country_method (product_id, country_code, shipping_method_id),
            INDEX idx_product (product_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """))

    # 4. Add weight/size columns to products (if not exists)
    for col_sql in [
        "ALTER TABLE products ADD COLUMN weight_kg DECIMAL(10,2) DEFAULT 0.5",
        "ALTER TABLE products ADD COLUMN length_cm DECIMAL(10,2)",
        "ALTER TABLE products ADD COLUMN width_cm DECIMAL(10,2)",
        "ALTER TABLE products ADD COLUMN height_cm DECIMAL(10,2)",
        "ALTER TABLE products ADD COLUMN shipping_category VARCHAR(50) DEFAULT 'standard'",
    ]:
        try:
            conn.execute(text(col_sql))
        except Exception:
            pass  # Column already exists

    # 5. Migrate existing product_shipping_rules data
    # Check if old table exists
    result = conn.execute(text("""
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema = DATABASE() AND table_name = 'product_shipping_rules'
    """))
    if result.scalar() > 0:
        print("Migrating existing product_shipping_rules data...")

        # Extract unique shipping methods
        rules = conn.execute(text("""
            SELECT DISTINCT shipping_method FROM product_shipping_rules WHERE shipping_method != ''
        """)).fetchall()

        for (method_name,) in rules:
            # Check if method already exists
            existing = conn.execute(text(
                "SELECT id FROM shipping_methods WHERE code = :code"
            ), {"code": method_name.upper().replace(" ", "_")}).first()

            if not existing:
                conn.execute(text("""
                    INSERT INTO shipping_methods (code, name, name_en)
                    VALUES (:code, :name, :name_en)
                """), {
                    "code": method_name.upper().replace(" ", "_"),
                    "name": method_name,
                    "name_en": method_name,
                })
                method_id = conn.execute(text(
                    "SELECT id FROM shipping_methods WHERE code = :code"
                ), {"code": method_name.upper().replace(" ", "_")}).scalar()
            else:
                method_id = existing[0]

            # Migrate rules for this method
            method_rules = conn.execute(text("""
                SELECT country, price, product_id FROM product_shipping_rules
                WHERE shipping_method = :method
            """), {"method": method_name}).fetchall()

            for country, price, product_id in method_rules:
                if country == "*":
                    # Default rule: apply to all active countries
                    countries = conn.execute(text(
                        "SELECT code FROM countries WHERE is_active = 1"
                    )).fetchall()
                    for (country_code,) in countries:
                        # Check if already exists
                        existing_rule = conn.execute(text("""
                            SELECT id FROM shipping_method_countries
                            WHERE shipping_method_id = :mid AND country_code = :cc
                        """), {"mid": method_id, "cc": country_code}).first()
                        if not existing_rule:
                            conn.execute(text("""
                                INSERT INTO shipping_method_countries
                                (shipping_method_id, country_code, base_fee, per_kg_fee, is_default)
                                VALUES (:mid, :cc, :base, 0, 1)
                            """), {"mid": method_id, "cc": country_code, "base": float(price)})
                else:
                    existing_rule = conn.execute(text("""
                        SELECT id FROM shipping_method_countries
                        WHERE shipping_method_id = :mid AND country_code = :cc
                    """), {"mid": method_id, "cc": country.upper()}).first()
                    if not existing_rule:
                        conn.execute(text("""
                            INSERT INTO shipping_method_countries
                            (shipping_method_id, country_code, base_fee, per_kg_fee)
                            VALUES (:mid, :cc, :base, 0)
                        """), {"mid": method_id, "cc": country.upper(), "base": float(price)})

        print(f"  Migrated {len(rules)} shipping method(s)")
        print("  Note: old product_shipping_rules table preserved for rollback")


def _run_sqlite_migration(conn):
    """SQLite migration (for local development)"""
    # SQLite doesn't support some ALTER TABLE operations, so we use IF NOT EXISTS style

    # 1. Create shipping_methods table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS shipping_methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code VARCHAR(50) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            name_en VARCHAR(100) NOT NULL,
            description TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """))

    # 2. Create shipping_method_countries table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS shipping_method_countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shipping_method_id INTEGER NOT NULL REFERENCES shipping_methods(id) ON DELETE CASCADE,
            country_code VARCHAR(10) NOT NULL,
            base_fee DECIMAL(10,2) NOT NULL,
            per_kg_fee DECIMAL(10,2) NOT NULL DEFAULT 0,
            min_weight_kg DECIMAL(10,2) DEFAULT 0.5,
            max_weight_kg DECIMAL(10,2),
            estimated_days_min INTEGER,
            estimated_days_max INTEGER,
            is_default INTEGER NOT NULL DEFAULT 0
        )
    """))

    # 3. Create product_shipping_overrides table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS product_shipping_overrides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            country_code VARCHAR(10) NOT NULL,
            shipping_method_id INTEGER NOT NULL REFERENCES shipping_methods(id),
            override_base_fee DECIMAL(10,2),
            override_per_kg_fee DECIMAL(10,2),
            surcharge DECIMAL(10,2) DEFAULT 0,
            is_disabled INTEGER NOT NULL DEFAULT 0
        )
    """))

    # 4. Add weight/size columns to products
    for col, default in [
        ("weight_kg", "0.5"),
        ("length_cm", "0.5"),
        ("width_cm", "0.5"),
        ("height_cm", "0.5"),
        ("shipping_category", "'standard'"),
    ]:
        try:
            conn.execute(text(f"ALTER TABLE products ADD COLUMN {col} DECIMAL(10,2) DEFAULT {default}"))
        except Exception:
            pass

    # 5. Migrate existing product_shipping_rules data
    try:
        rules = conn.execute(text("""
            SELECT DISTINCT shipping_method FROM product_shipping_rules WHERE shipping_method != ''
        """)).fetchall()

        for (method_name,) in rules:
            code = method_name.upper().replace(" ", "_")
            existing = conn.execute(text(
                "SELECT id FROM shipping_methods WHERE code = :code"
            ), {"code": code}).first()

            if not existing:
                conn.execute(text("""
                    INSERT INTO shipping_methods (code, name, name_en)
                    VALUES (:code, :name, :name_en)
                """), {"code": code, "name": method_name, "name_en": method_name})
                method_id = conn.execute(text(
                    "SELECT id FROM shipping_methods WHERE code = :code"
                ), {"code": code}).scalar()
            else:
                method_id = existing[0]

            method_rules = conn.execute(text("""
                SELECT country, price, product_id FROM product_shipping_rules
                WHERE shipping_method = :method
            """), {"method": method_name}).fetchall()

            for country, price, product_id in method_rules:
                if country == "*":
                    countries = conn.execute(text(
                        "SELECT code FROM countries WHERE is_active = 1"
                    )).fetchall()
                    for (country_code,) in countries:
                        existing_rule = conn.execute(text("""
                            SELECT id FROM shipping_method_countries
                            WHERE shipping_method_id = :mid AND country_code = :cc
                        """), {"mid": method_id, "cc": country_code}).first()
                        if not existing_rule:
                            conn.execute(text("""
                                INSERT INTO shipping_method_countries
                                (shipping_method_id, country_code, base_fee, per_kg_fee, is_default)
                                VALUES (:mid, :cc, :base, 0, 1)
                            """), {"mid": method_id, "cc": country_code, "base": float(price)})
                else:
                    existing_rule = conn.execute(text("""
                        SELECT id FROM shipping_method_countries
                        WHERE shipping_method_id = :mid AND country_code = :cc
                    """), {"mid": method_id, "cc": country.upper()}).first()
                    if not existing_rule:
                        conn.execute(text("""
                            INSERT INTO shipping_method_countries
                            (shipping_method_id, country_code, base_fee, per_kg_fee)
                            VALUES (:mid, :cc, :base, 0)
                        """), {"mid": method_id, "cc": country.upper(), "base": float(price)})

        print(f"  Migrated {len(rules)} shipping method(s)")
    except Exception as e:
        print(f"  Note: Could not migrate old rules (table may not exist): {e}")


if __name__ == "__main__":
    migrate()
