from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, EmailStr


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: str
    tenant_id: uuid.UUID | None = None


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "owner"
