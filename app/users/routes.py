from fastapi import APIRouter, HTTPException, status
from app.users.schemas import UserOut, PatchPasswordRequest, PatchStatusRequest
from app.users import services

userRoutes = APIRouter(prefix="/users")

@userRoutes.patch("/{id}/password", response_model=UserOut)
def modifyPassword(id:int, payload: PatchPasswordRequest):
    try:
        return services.modifyUserPassword(id, oldPassword=payload.old_password, newPassword=payload.new_password)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@userRoutes.patch("/{id}/status", response_model=UserOut)
def modifyStatus(id:int, payload: PatchStatusRequest):
    try:
        return services.modifyUserStatus(id, payload.status)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))