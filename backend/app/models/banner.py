from sqlalchemy import Column, Integer, String, DateTime, func

from app.models import Base


class Banner(Base):
    """首页轮播横幅"""
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tag = Column(String(50))  # 如 "MEGA SALE"
    title = Column(String(255), nullable=False)  # 主标题
    subtitle = Column(String(255))  # 副标题/描述
    image_url = Column(String(500))  # 背景图片 URL
    button_text = Column(String(50), default="Shop Now")  # 按钮文字
    button_link = Column(String(255), default="/browse")  # 按钮链接
    bg_color_from = Column(String(20), default="#FF5000")  # 渐变起始色
    bg_color_to = Column(String(20), default="#FF6B35")  # 渐变结束色
    is_active = Column(Integer, default=1, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
