from pydantic import BaseModel, Field

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)

class RegisterResponse(BaseModel):
    id: int
    name: str
    password: str

class LoginRequest(BaseModel):
    name: str
    password: str