"""买家认证路由 — 注册、登录(统一)、个人资料"""
from datetime import datetime, timedelta
import hashlib
import secrets
import smtplib
from email.message import EmailMessage
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import hash_password, verify_password, create_access_token, settings
from app.schemas import (
    LoginRequest, UserRegister, UserProfileUpdate, UserOut, TokenResponse,
    PasswordResetRequest, PasswordResetConfirm,
    EmailVerificationConfirm,
)
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, PasswordResetToken, EmailVerificationToken
from app.schemas import UserRegister, UserProfileUpdate, UserOut, TokenResponse

router = APIRouter()


def _send_password_reset_email(recipient: str, raw_token: str):
    if not settings.smtp_host or not settings.smtp_from_email:
        return False
    link = f"{settings.frontend_url.rstrip('/')}/forgot-password?token={quote(raw_token)}"
    message = EmailMessage()
    message["Subject"] = "Reset your BeCool password"
    message["From"] = settings.smtp_from_email
    message["To"] = recipient
    message.set_content(f"Use this link within 30 minutes to reset your BeCool password:\n\n{link}\n")
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as client:
        if settings.smtp_use_tls:
            client.starttls()
        if settings.smtp_username:
            client.login(settings.smtp_username, settings.smtp_password)
        client.send_message(message)
    return True


def _send_email_verification(recipient: str, raw_token: str):
    if not settings.smtp_host or not settings.smtp_from_email:
        return False
    link = f"{settings.frontend_url.rstrip('/')}/verify-email?token={quote(raw_token)}"
    message = EmailMessage()
    message["Subject"] = "Verify your BeCool email"
    message["From"] = settings.smtp_from_email
    message["To"] = recipient
    message.set_content(f"Verify your BeCool email within 24 hours:\n\n{link}\n")
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as client:
        if settings.smtp_use_tls:
            client.starttls()
        if settings.smtp_username:
            client.login(settings.smtp_username, settings.smtp_password)
        client.send_message(message)
    return True


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(req: UserRegister, db: Session = Depends(get_db)):
    """买家注册 — 注册成功自动登录"""
    if len(req.password) < 8 or not any(char.isalpha() for char in req.password) or not any(char.isdigit() for char in req.password):
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters and include a letter and a number")
    if not req.email:
        raise HTTPException(status_code=400, detail="Email is required")
    if settings.environment.lower() == "production" and (not settings.smtp_host or not settings.smtp_from_email):
        raise HTTPException(status_code=503, detail="Email verification is temporarily unavailable")
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

    raw_token = secrets.token_urlsafe(32)
    db.add(EmailVerificationToken(
        user_id=user.id,
        token_hash=hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
        expires_at=datetime.utcnow() + timedelta(hours=24),
    ))
    db.commit()
    if settings.smtp_host and settings.smtp_from_email:
        try:
            _send_email_verification(user.email, raw_token)
        except (OSError, smtplib.SMTPException):
            if settings.environment.lower() == "production":
                db.query(EmailVerificationToken).filter(EmailVerificationToken.user_id == user.id).delete()
                db.delete(user)
                db.commit()
                raise HTTPException(status_code=503, detail="Verification email could not be sent")
    response = {
        "access_token": None,
        "token_type": "bearer",
        "user": UserOut.model_validate(user),
        "verification_required": True,
    }
    if settings.environment.lower() != "production" and not settings.smtp_host:
        response["email_verification_token"] = raw_token
    return response


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """统一登录 — 管理员和买家均可使用"""
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")
    pending_verification = db.query(EmailVerificationToken.id).filter(
        EmailVerificationToken.user_id == user.id,
        EmailVerificationToken.used_at.is_(None),
    ).first()
    if pending_verification:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please verify your email before signing in")

    token = create_access_token(
        data={"sub": user.id, "role": user.role},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserOut.model_validate(user),
    }


@router.post("/email-verification/confirm", response_model=TokenResponse)
def confirm_email_verification(data: EmailVerificationConfirm, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(data.token.encode("utf-8")).hexdigest()
    token = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token_hash == token_hash,
        EmailVerificationToken.used_at.is_(None),
        EmailVerificationToken.expires_at > datetime.utcnow(),
    ).first()
    if not token:
        raise HTTPException(status_code=400, detail="Verification link is invalid or expired")
    user = db.query(User).filter(User.id == token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")
    token.used_at = datetime.utcnow()
    db.commit()
    access_token = create_access_token(
        data={"sub": user.id, "role": user.role},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {"access_token": access_token, "token_type": "bearer", "user": UserOut.model_validate(user)}


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


@router.post("/password-reset/request")
def request_password_reset(data: PasswordResetRequest, db: Session = Depends(get_db)):
    if settings.environment.lower() == "production" and (not settings.smtp_host or not settings.smtp_from_email):
        raise HTTPException(status_code=503, detail="Password reset email is temporarily unavailable")
    account = data.account.strip()
    user = db.query(User).filter(
        (User.username == account) | (User.email == account)
    ).first()
    response = {"message": "If that account exists, reset instructions are ready."}
    if not user:
        return response

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used_at.is_(None),
    ).delete()
    db.add(PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(minutes=30),
    ))
    db.commit()

    if user.email and settings.smtp_host and settings.smtp_from_email:
        try:
            _send_password_reset_email(user.email, raw_token)
        except (OSError, smtplib.SMTPException):
            if settings.environment.lower() == "production":
                raise HTTPException(status_code=503, detail="Password reset email is temporarily unavailable")

    # Local development has no mail provider. Returning the token keeps the
    # complete reset flow testable; production responses never expose it.
    if settings.environment.lower() != "production" and not settings.smtp_host:
        response["reset_token"] = raw_token
    return response


@router.post("/password-reset/confirm")
def confirm_password_reset(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    if len(data.new_password) < 8 or not any(char.isalpha() for char in data.new_password) or not any(char.isdigit() for char in data.new_password):
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters and include a letter and a number")
    token_hash = hashlib.sha256(data.token.encode("utf-8")).hexdigest()
    token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash,
        PasswordResetToken.used_at.is_(None),
        PasswordResetToken.expires_at > datetime.utcnow(),
    ).first()
    if not token:
        raise HTTPException(status_code=400, detail="Reset link is invalid or expired")
    user = db.query(User).filter(User.id == token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")
    user.password_hash = hash_password(data.new_password)
    token.used_at = datetime.utcnow()
    db.commit()
    return {"message": "Password updated. You can now sign in."}
