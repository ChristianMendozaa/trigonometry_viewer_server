from pydantic import BaseModel
from enum import Enum

class UserRole(str, Enum):
    user = "user"
    admin = "admin"

class User(BaseModel):
    id: str
    name: str
    email: str
    role: UserRole
