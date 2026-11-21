from app.users.schemas import UserStatus
from sqlmodel import Session, select
from app.models import User
from app.auth.security import createAccessToken
import secrets


def register_user(session: Session, name: str):
    existing = session.exec(select(User).where(User.name == name)).first()
    if existing:
      raise ValueError("name already taken")

    password = secrets.token_urlsafe(8)
    newUser=User(name= name, password=password)

    session.add(newUser)
    session.commit()
    session.refresh(newUser)

    return newUser

def authenticate_user(session: Session, name: str, password: str):
      user = session.exec(select(User).where(User.name==name)).first()
      if not user or user.password != password:
            raise ValueError("Invalid name or password")
      if user.status==UserStatus.BLOCKED.value:
            raise PermissionError("User account is blocked")

      token = createAccessToken(user.id, user.role)
      return {"access_token":token, "user":user}
