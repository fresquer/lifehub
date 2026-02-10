from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str | None = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None


# --- Area ---

class AreaCreate(BaseModel):
    name: str
    description: str | None = None


class AreaUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class AreaResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Project ---

class ProjectCreate(BaseModel):
    area_id: int
    name: str
    icon: str | None = None
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    icon: str | None = None
    description: str | None = None
    area_id: int | None = None


class ProjectResponse(BaseModel):
    id: int
    area_id: int
    icon: str | None
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
