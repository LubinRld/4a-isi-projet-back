from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session
from app.database import get_session
from app.models import User
from app.users.schemas import UserRole, UserStatus
from app.auth.security import decodeAccessToken

bearerScheme = HTTPBearer()


def getCurrentUser(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearerScheme)],
    session: Annotated[Session, Depends(get_session)]):
    try:
        payload = decodeAccessToken(credentials.credentials)
        sub = payload.get("sub")
        if sub is None:
            raise ValueError("Invalid token payload")
        userId = int(sub)
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    user = session.get(User, userId)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    if user.status != UserStatus.ACTIVE.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is blocked")
    return user

def requireAdmin(
    currentUser: Annotated[User, Depends(getCurrentUser)]):
    if currentUser.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator privileges required")
    return currentUser