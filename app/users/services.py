from sqlmodel import Session, select, func
from app.users.schemas import UserStatus
from app.models import User

def getAllUsers(session: Session, limit: int = 20, offset: int =0):
    getAllUsersStatement = select(User).limit(limit).offset(offset)
    users = session.exec(getAllUsersStatement).all()
    getTotalUsersStatement = select(func.count()).select_from(User)
    total = session.exec(getTotalUsersStatement).one()
    return {
        "total":total,
        "limit": limit,
        "offset": offset,
        "data": users
    }
    
def modifyUserPassword(session: Session, userId: int, oldPassword:str, newPassword: str):
    user = session.get(User, userId)
    if user is None:
        raise LookupError("User not found")
    if user.status==UserStatus.BLOCKED:
        raise PermissionError("User account is blocked")
    if user.password!=oldPassword:
        raise ValueError("Invalid old password")
    if user.password == newPassword:
        raise ValueError("New password must be different from old password")

    user.password = newPassword
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def modifyUserStatus(session: Session, userId: int, status: UserStatus, adminId: int):
    if userId == adminId:
        raise PermissionError("Admin cannot change their own account status")
    user = session.get(User, userId)

    if user is None: 
        raise LookupError("User not found")
    if user.status==status:
        raise ValueError(f"User account is already {status.value}")

    user.status=status.value
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

