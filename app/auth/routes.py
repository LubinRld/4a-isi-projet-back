from fastapi import APIRouter, HTTPException, status
from app.auth import services
from app.auth.schemas import (LoginRequest, RegisterRequest, RegisterResponse, UserOut)

authRoutes = APIRouter(prefix="/auth")

@authRoutes.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest):
    try:
        return services.register_user(payload.username)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@authRoutes.post("/login", response_model=UserOut)
def login(payload: LoginRequest):
    try:
        return services.authenticate_user(payload.username, payload.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(e)
        )
        