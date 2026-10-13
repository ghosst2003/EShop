"""Add product transaction details and immutable meetup snapshots to orders.

Usage: cd backend && python migrate_transaction_modes.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import inspect, text

from app.database import engine


PRODUCT_COLUMNS = {
    "pickup_location": "VARCHAR(300) NULL",
    "pickup_schedule": "VARCHAR(300) NULL",
    "pickup_instructions": "TEXT NULL",
}

ORDER_COLUMNS = {
    "transaction_mode": "VARCHAR(20) NOT NULL DEFAULT 'online'",
    "pickup_location": "VARCHAR(300) NULL",
    "pickup_schedule": "VARCHAR(300) NULL",
    "pickup_contact": "VARCHAR(200) NULL",
    "pickup_payment": "TEXT NULL",
    "pickup_instructions": "TEXT NULL",
}


def _add_missing_columns(conn, table_name: str, definitions: dict[str, str]) -> None:
    existing = {column["name"] for column in inspect(conn).get_columns(table_name)}
    for name, definition in definitions.items():
        if name not in existing:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {name} {definition}"))
            print(f"  Added {table_name}.{name}")


def migrate() -> None:
    with engine.begin() as conn:
        _add_missing_columns(conn, "products", PRODUCT_COLUMNS)
        _add_missing_columns(conn, "orders", ORDER_COLUMNS)
        conn.execute(text(
            "UPDATE orders SET transaction_mode = CASE "
            "WHEN payment_method = 'in_person' THEN 'in_person' ELSE 'online' END "
            "WHERE transaction_mode IS NULL OR transaction_mode = ''"
        ))
    print("Transaction mode migration completed.")


if __name__ == "__main__":
    migrate()
