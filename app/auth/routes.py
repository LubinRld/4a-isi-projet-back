from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated
from sqlmodel import Session
from app.database import get_session
from app.auth import services
from app.auth.schemas import LoginRequest, RegisterRequest, RegisterResponse, TokenResponse

authRoutes = APIRouter(prefix="/auth")

@authRoutes.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(session : Annotated[Session, Depends(get_session)], payload: RegisterRequest):
    try:
        return services.register_user(session, payload.name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@authRoutes.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(session: Annotated[Session, Depends(get_session)], payload: LoginRequest):
    try:
        return services.authenticate_user(session, payload.name, payload.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        