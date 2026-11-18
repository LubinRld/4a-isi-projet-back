from pydantic import BaseModel, Field

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)

class RegisterResponse(BaseModel):
    id: int
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str