from sqlalchemy import Column, Integer, String, DateTime, func

from app.models import Base


class Country(Base):
    """国家/地区配置表"""
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False)  # ISO 3166-1 alpha-2
    name = Column(String(100), nullable=False)  # 中文名
    name_en = Column(String(100), nullable=False)  # 英文名
    flag_emoji = Column(String(10))  # 国旗 emoji
    is_active = Column(Integer, default=1, nullable=False)
    pickup_enabled = Column(Integer, default=0, nullable=False)  # 是否允许面对面交易
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
