from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User, UserRole
from app.models.nodes import Student


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_token(user_id: int, token_type: str = "access") -> str:
    if token_type == "access":
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire)
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.refresh_token_expire)
    payload = {"sub": str(user_id), "type": token_type, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return payload
    except JWTError:
        return None


async def register_user(
    db: AsyncSession,
    email: str,
    password: str,
    name: str,
    role: str,
    grade_level: int | None = None,
) -> User:
    # Check duplicate email
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise ValueError("Email already registered")

    user_role = UserRole(role)

    # If student role, create Student record first
    student_id = None
    if user_role == UserRole.student:
        student = Student(name=name, grade_level=grade_level)
        db.add(student)
        await db.flush()
        student_id = student.id

    user = User(
        email=email,
        hashed_password=hash_password(password),
        name=name,
        role=user_role,
        student_id=student_id,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
