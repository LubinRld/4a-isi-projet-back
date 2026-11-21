from fastapi import APIRouter, HTTPException, status, Query, Depends
from app.models import User
from app.users.schemas import UserOut, PatchPasswordRequest, PatchStatusRequest, GetUsersQuery
from app.shared.schemas import PaginatedResponse
from app.users import services
from typing import Annotated
from sqlmodel import Session
from app.database import get_session
from app.auth.dependencies import getCurrentUser, requireAdmin

userRoutes = APIRouter(prefix="/users")

@userRoutes.get("", response_model=PaginatedResponse[UserOut], status_code=status.HTTP_200_OK)
def getAllUsers(
    session: Annotated[Session, Depends(get_session)], 
    query: Annotated[GetUsersQuery, Query()],
    admin: Annotated[User, Depends(requireAdmin)]):
    return services.getAllUsers(session, query.limit, query.offset)

@userRoutes.patch("/{user_id}/password", response_model=UserOut, status_code=status.HTTP_200_OK)
def modifyPassword(
    session: Annotated[Session, Depends(get_session)], 
    user_id:int, 
    payload: PatchPasswordRequest,
    currentUser: Annotated[User, Depends(getCurrentUser)]):

    if currentUser.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only modify your own password")
    try:
        return services.modifyUserPassword(session, user_id, oldPassword=payload.old_password, newPassword=payload.new_password)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@userRoutes.patch("/{user_id}/status", response_model=UserOut, status_code=status.HTTP_200_OK)
def modifyStatus(
    session: Annotated[Session, Depends(get_session)],
    user_id:int, 
    payload: PatchStatusRequest,
    admin: Annotated[User, Depends(requireAdmin)]):
    try:
        return services.modifyUserStatus(session, user_id, payload.status, adminId= admin.id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= str(e))