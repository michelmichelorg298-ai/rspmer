from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserInDB(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    hashed_password: str
    role: str
    disabled: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "read"


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    disabled: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    old_password: str
    new_password: str
