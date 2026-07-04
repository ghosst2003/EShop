"""买家认证路由 — 注册、登录(统一)、个人资料"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import hash_password, verify_password, create_access_token, settings
from app.schemas import LoginRequest, UserRegister, UserProfileUpdate, UserOut, TokenResponse
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import UserRegister, UserProfileUpdate, UserOut, TokenResponse

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(req: UserRegister, db: Session = Depends(get_db)):
    """买家注册 — 注册成功自动登录"""
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    if req.email and db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        role="buyer",
        display_name=req.display_name or req.username,
        email=req.email,
        phone=req.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        data={"sub": user.id, "role": user.role},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserOut.model_validate(user),
    }


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """统一登录 — 管理员和买家均可使用"""
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    token = create_access_token(
        data={"sub": user.id, "role": user.role},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserOut.model_validate(user),
    }


@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return user


@router.put("/profile", response_model=UserOut)
def update_profile(
    data: UserProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新个人资料 — 仅买家可操作"""
    if user.role != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can update profile")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user
