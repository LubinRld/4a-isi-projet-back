import argparse
import getpass
import sys
from sqlmodel import Session, select
from app.database import engine
from app.models import User
from app.users.schemas import UserRole, UserStatus
from app.auth.security import hashPassword


def createAdmin(session: Session, name: str, password: str) -> User:
    cleanName = name.strip()
    if len(cleanName) < 3 or len(cleanName) > 32:
        raise ValueError("Username must be between 3 and 32 characters")

    if len(password) < 3:
        raise ValueError("Password must be at least 3 characters long")

    existingUser = session.exec(
        select(User).where(User.name == cleanName)
    ).first()
    if existingUser is not None:
        raise ValueError(f"User '{cleanName}' already exists")

    adminUser = User(
        name=cleanName,
        role=UserRole.ADMIN.value,
        status=UserStatus.ACTIVE.value,
        password=hashPassword(password),
    )

    session.add(adminUser)
    session.commit()
    session.refresh(adminUser)
    return adminUser


def parseArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an administrator account for Pol-eat-heck."
    )
    parser.add_argument(
        "name",
        type=str,
        help="Administrator username (3 to 32 characters)",
    )
    return parser.parse_args()


def main() -> None:
    args = parseArgs()
    password = getpass.getpass("Admin password: ")
    confirmPassword = getpass.getpass("Confirm admin password: ")

    if password != confirmPassword:
        print("Error: Passwords do not match.", file=sys.stderr)
        sys.exit(1)

    try:
        with Session(engine) as session:
            admin = createAdmin(session, args.name, password)
            print(f"Admin '{admin.name}' created successfully (id={admin.id}).")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()