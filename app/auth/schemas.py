from pydantic import BaseModel, Field
from app.users.schemas import UserOut


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=32)

class RegisterResponse(BaseModel):
    id: int
    name: str
    password: str

class LoginRequest(BaseModel):
    name: str
    password: str

class TokenResponse(BaseModel):
    access_token:str
    user: UserOut