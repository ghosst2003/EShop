"""
Migration: Add face-to-face deal (local pickup) support
- Add pickup_enabled, pickup_contact, pickup_payment columns to products table
- Add pickup_enabled column to countries table

Usage: cd backend && python migrate_pickup.py
"""
import sys
from pathlib import Path

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
    print("✅ Pickup migration completed successfully.")


def _run_mysql_migration(conn):
    """MySQL migration"""
    # 1. Add pickup columns to products
    for col_sql in [
        "ALTER TABLE products ADD COLUMN pickup_enabled TINYINT(1) NOT NULL DEFAULT 0",
        "ALTER TABLE products ADD COLUMN pickup_contact VARCHAR(200) NULL",
        "ALTER TABLE products ADD COLUMN pickup_payment TEXT NULL",
    ]:
        try:
            conn.execute(text(col_sql))
        except Exception:
            pass  # Column already exists

    # 2. Add pickup_enabled to countries
    try:
        conn.execute(text(
            "ALTER TABLE countries ADD COLUMN pickup_enabled TINYINT(1) NOT NULL DEFAULT 0"
        ))
    except Exception:
        pass  # Column already exists

    print("  Added pickup fields to products and countries tables")


def _run_sqlite_migration(conn):
    """SQLite migration (for local development)"""
    # Products table
    for col in ["pickup_enabled", "pickup_contact", "pickup_payment"]:
        try:
            conn.execute(text(f"ALTER TABLE products ADD COLUMN {col} INTEGER DEFAULT 0"))
        except Exception:
            pass  # Column already exists

    # Countries table
    try:
        conn.execute(text("ALTER TABLE countries ADD COLUMN pickup_enabled INTEGER DEFAULT 0"))
    except Exception:
        pass  # Column already exists

    print("  Added pickup fields to products and countries tables (SQLite)")


if __name__ == "__main__":
    migrate()
