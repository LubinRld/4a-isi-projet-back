from app.database import FAKE_USERS_DB
from app.users.schemas import UserStatus

def modifyUserPassword(userId: int, oldPassword:str, newPassword: str):
    user = next((user for user in FAKE_USERS_DB if user["id"]==userId), None)
    if user is None:
        raise LookupError("User not found")
    if user["status"]==UserStatus.BLOCKED:
        raise PermissionError("User account is blocked")
    if user["password"]!=oldPassword:
        raise ValueError("Invalid old password")
    if user["password"] == newPassword:
        raise ValueError("New password must be different from old password")

    user["password"]= newPassword
    return user

def modifyUserStatus(userId: int, status: UserStatus):
    user = next((user for user in FAKE_USERS_DB if user["id"]==userId), None)

    if user is None: 
        raise LookupError("User not found")
    if user["status"]==status:
        raise ValueError(f"User account is already {status.value}")

    user["status"]=status
    return user

