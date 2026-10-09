from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    # The hosted MySQL service closes idle connections sooner than SQLAlchemy's
    # default lifetime. Recycle them before the server can hand us a stale one.
    pool_recycle=300,
    pool_timeout=20,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
