from datetime import date
from pydantic import BaseModel, validator, ValidationError
from enum import Enum


class CommentStatus(str, Enum):
    PUBLICATED = "PUBLICATED"
    DECLINED = "DECLINED"

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"
    EDITOR = "EDITOR"
    WRITER = "WRITER"
    DEFAULT = "DEFAULT"
    BANNED = "BANNED"

ROLES_SET = {UserRole.ADMIN, UserRole.MODERATOR, UserRole.EDITOR, UserRole.WRITER, UserRole.DEFAULT}

class Roles(BaseModel):
    @classmethod
    def add_role(cls, roles: str, role: UserRole):
        if role in roles:
            return None
        roles = list(roles.strip().split(';'))
        roles.append(role)
        return ';'.join(sorted(roles))

    @classmethod
    def delete_role(cls, roles: str, role: UserRole):
        if role not in roles:
            return None
        roles = list(roles.strip().split(';'))
        roles.remove(role)
        return ';'.join(sorted(roles))

    @classmethod
    def compare_role(cls, roles: str, role_to_compare: UserRole):
        if len(roles) == 0:
            return None
        roles = list(roles.strip().split(';'))
        return role_to_compare in roles

    @classmethod
    def compare_roles(cls, roles: str, roles_to_compare: tuple):
        if len(roles) == 0:
            return None
        roles = set(roles.strip().split(';'))
        roles_to_compare = set(roles_to_compare)
        return len(roles & roles_to_compare)

    @classmethod
    def ban(cls, roles: str):
        return UserRole.BANNED

    role: UserRole
    @validator('role')
    def validate_role(cls, role):
        roles = set(role.strip().split(';'))
        if not roles <= ROLES_SET:
            raise ValidationError
        return role

class BaseComment(BaseModel):
    text: str

class Comment(BaseComment):
    id: int
    user_id: int
    article_id: int
    status:CommentStatus

    class Config:
        orm_mode = True

class BaseUser(BaseModel):
    email: str
    username: str
    role: UserRole

    @validator('role')
    def validate_role(cls, role):
        roles = set(role.strip().split(';'))
        if not roles <= ROLES_SET:
            raise ValidationError
        return role


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