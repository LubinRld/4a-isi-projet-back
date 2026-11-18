from app.users.schemas import UserRole, UserStatus
from app.database import FAKE_USERS_DB
import secrets


def register_user(username: str):
    if any(user["username"] == username for user in FAKE_USERS_DB):
           raise ValueError("Username already taken")

    password = secrets.token_urlsafe(8)

    new_user={"id": len(FAKE_USERS_DB)+1,
              "username": username,
              "password": password,
              "role": UserRole.USER,
              "status": UserStatus.ACTIVE
              }

    FAKE_USERS_DB.append(new_user)

    return {
          "id": new_user["id"],
          "username": new_user["username"],
          "password": password
    }

def authenticate_user(username: str, password: str):
      user = next((user for user in FAKE_USERS_DB if user["username"] == username), None)
      if not user or user["password"] != password:
            raise ValueError("Invalid username or password")
      if user["status"]==UserStatus.BLOCKED:
            raise PermissionError("User account is blocked")
      return user
