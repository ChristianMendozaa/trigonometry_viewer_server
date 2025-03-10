from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: Optional[str] = "user"

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str
