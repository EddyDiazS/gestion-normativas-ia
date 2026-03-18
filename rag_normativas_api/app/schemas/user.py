from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: str
    role: str
    faculty: Optional[str] = None
    program: Optional[str] = None

class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    faculty: Optional[str] = None
    program: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True