from pydantic import BaseModel, Field
from enum import Enum
from app.shared.schemas import PaginationQuery

class GetUsersQuery(PaginationQuery):
    pass

class UserStatus(str, Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class UserOut(BaseModel):
    id: int
    name: str
    role: UserRole
    status: UserStatus

class PatchPasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=3)
    new_password:str = Field(..., min_length=3)

class PatchStatusRequest(BaseModel):
    status: UserStatus