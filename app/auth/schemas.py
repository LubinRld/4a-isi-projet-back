from pydantic import BaseModel, Field
from enum import Enum

class UserStatus(str, Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)

class RegisterResponse(BaseModel):
    id: int
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    role: UserRole
    status: UserStatus