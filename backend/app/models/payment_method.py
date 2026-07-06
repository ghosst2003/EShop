from sqlalchemy import Column, Integer, String, DateTime, func

from app.models import Base


class PaymentMethod(Base):
    """支持的支付方式"""
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)  # 如 "paypal", "visa", "mastercard"
    name = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=False)
    logo_url = Column(String(500))  # 支付图标 URL
    color = Column(String(20))  # 图标主色（用于无 logo 时的背景色）
    text_color = Column(String(20))  # 文字颜色
    is_active = Column(Integer, default=1, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
