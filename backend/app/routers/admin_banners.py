import uuid
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Banner
from app.schemas import BannerCreate, BannerUpdate, BannerOut

router = APIRouter()
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads" / "banners"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("", response_model=list[BannerOut])
def list_banners(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """获取 Banner 列表"""
    return db.query(Banner).order_by(Banner.sort_order, Banner.created_at.desc()).all()


@router.post("", response_model=BannerOut)
def create_banner(
    data: BannerCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """创建 Banner"""
    banner = Banner(
        tag=data.tag,
        title=data.title,
        subtitle=data.subtitle,
        image_url=data.image_url,
        button_text=data.button_text,
        button_link=data.button_link,
        bg_color_from=data.bg_color_from,
        bg_color_to=data.bg_color_to,
        is_active=1 if data.is_active else 0,
        sort_order=data.sort_order,
    )
    db.add(banner)
    db.commit()
    db.refresh(banner)
    return banner


@router.put("/{banner_id}", response_model=BannerOut)
def update_banner(
    banner_id: int,
    data: BannerUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """更新 Banner"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "is_active":
            setattr(banner, field, 1 if value else 0)
        else:
            setattr(banner, field, value)

    db.commit()
    db.refresh(banner)
    return banner


@router.post("/{banner_id}/image", response_model=BannerOut)
def upload_banner_image(
    banner_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """上传 Banner 背景图片"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")

    ext = Path(file.filename).suffix if file.filename else ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = UPLOAD_DIR / filename
    filepath.write_bytes(file.file.read())

    banner.image_url = f"/uploads/banners/{filename}"
    db.commit()
    db.refresh(banner)
    return banner


@router.delete("/{banner_id}")
def delete_banner(
    banner_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """删除 Banner"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    db.delete(banner)
    db.commit()
    return {"message": "Banner deleted"}
