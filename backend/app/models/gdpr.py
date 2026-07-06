from sqlalchemy import Column, String, Text, BigInteger, Enum, DateTime, ForeignKey, Integer, func

from app.models import Base


class GdprConsentLog(Base):
    __tablename__ = "gdpr_consent_logs"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(128), nullable=False)
    consent_type = Column(Enum("cookie", "newsletter", "data_processing"), nullable=False)
    consent_given = Column(Integer, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class DataDeletionRequest(Base):
    __tablename__ = "data_deletion_requests"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), nullable=False)
    request_type = Column(Enum("data_export", "data_deletion", "rectification"), nullable=False)
    details = Column(Text)
    status = Column(
        Enum("pending", "in_progress", "completed", "rejected"),
        default="pending",
        nullable=False,
    )
    admin_notes = Column(Text)
    processed_by = Column(Integer, ForeignKey("users.id"))
    processed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
