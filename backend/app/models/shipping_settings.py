from sqlalchemy import Column, Integer, String, DateTime, func

from app.models import Base


class GlobalShippingSettings(Base):
    """全局 shipping info 区域设置"""
    __tablename__ = "global_shipping_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    show_combined_shipping = Column(Integer, default=1, nullable=False)  # 是否显示 "Save on combined shipping"
    combined_shipping_text = Column(String(200), default="Save on combined shipping")  # 提示文案
    show_import_fees = Column(Integer, default=1, nullable=False)  # 是否显示 Import fees
    import_fees_text = Column(String(200), default="Import fees may apply on delivery")  # Import fees 文案
    section_title = Column(String(100), default="Shipping, returns, and payments")  # 区块标题
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
