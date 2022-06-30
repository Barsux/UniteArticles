from datetime import date
from pydantic import BaseModel
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"
    EDITOR = "EDITOR"
    WRITER = "WRITER"
    DEFAULT = "DEFAULT"


class BaseUser(BaseModel):
    email: str
    username: str
    role: UserRole


class UserCreate(BaseUser):
    role = UserRole.DEFAULT
    password: str


class User(BaseUser):
    id: int

    class Config:
        orm_mode = True

class UserUpdate(User):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"