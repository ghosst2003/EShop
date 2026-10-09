from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel


# ---- Auth ----
class LoginRequest(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    password: str
    display_name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None


class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional["UserOut"] = None
    verification_required: bool = False
    email_verification_token: Optional[str] = None


class UserOut(BaseModel):
    id: int
    username: str
    display_name: str
    role: str
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None

    model_config = {"from_attributes": True}


class PasswordResetRequest(BaseModel):
    account: str


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class EmailVerificationConfirm(BaseModel):
    token: str
