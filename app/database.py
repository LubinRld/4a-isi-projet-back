from app.users.schemas import UserRole, UserStatus

FAKE_USERS_DB: list[dict] = [
    {
        "id":1,
        "username": "admin",
        "password": "admin123",
        "role": UserRole.ADMIN,
        "status": UserStatus.ACTIVE
    }]