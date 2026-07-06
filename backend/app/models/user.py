from sqlalchemy import Column, Integer, String, DateTime, Enum, func
from sqlalchemy.orm import relationship

from app.models import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("admin", "buyer", name="user_role"), default="admin", nullable=False)
    display_name = Column(String(100), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    avatar = Column(String(500))
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    products = relationship("Product", back_populates="creator")
    created_orders = relationship("Order", foreign_keys="Order.created_by", back_populates="creator")
    buyer_orders = relationship("Order", foreign_keys="Order.buyer_id", back_populates="buyer")
    cart = relationship("Cart", back_populates="buyer", uselist=False)
    addresses = relationship("Address", back_populates="buyer", cascade="all, delete-orphan")
