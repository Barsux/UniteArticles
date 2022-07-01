import time

import sqlalchemy.exc

from app.models.auth import User, UserCreate, Roles, UserRole, Token
from app.settings import settings
from passlib.hash import bcrypt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from app import tables
from datetime import datetime
from app.database import get_session
from sqlalchemy.orm import Session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/sign-in/')

def get_curr_user(token: str = Depends(oauth2_scheme)) -> User:
    return AuthService.verify_token(token)

class AuthService:
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(plain_password, hashed_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt.hash(password)

    @classmethod
    def verify_token(cls, token: str) -> User:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
            )
        except JWTError:
            raise exception from None

        user_data = payload.get('user')

        try:
            user = User.parse_obj(user_data)
        except ValidationError:
            raise exception from None
        return user

    @classmethod
    def create_token(cls, user: tables.User) -> Token:
        user_data = User.from_orm(user)
        now = time.time()
        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + settings.jwt_ttl,
            'sub': str(user_data.id),
            'user': user_data.dict()
        }
        token = jwt.encode(
            payload,
            settings.jwt_secret,
            settings.jwt_algorithm
        )
        return Token(access_token=token)

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def raise_401_with_text(self, text):
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=text,
            headers={'WWW-Authentificate': 'Bearer'}
        )
        raise exception from None

    def _get_by_id(self, user_id) -> User:
        operation = (
            self.session
                .query(tables.User)
                .filter_by(id=user_id)
                .first()
        )
        if not operation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return operation

    def register(self, user_data: UserCreate) -> Token:
        user = tables.User(
            email=user_data.email,
            username=user_data.username,
            password=self.hash_password(user_data.password),
            role=UserRole.DEFAULT
        )
        self.session.add(user)
        try:
            self.session.commit()
        except sqlalchemy.exc.IntegrityError:
            self.raise_401_with_text("User with same nickname already registered")
        return self.create_token(user)

    def login(self, username: str, password: str) -> Token:
        user = (
            self.session
            .query(tables.User)
            .filter(tables.User.username == username)
            .first()
        )
        if not user:
            self.raise_401_with_text("Incorrect username")

        if not self.verify_password(password, user.password):
            self.raise_401_with_text("Incorrect password")

        return self.create_token(user)

    def get_user(self, user: User, user_id: int) -> User:
        return self._get_by_id(user_id)

    def update_user(self, user: User, user_data: User) -> User:
        db_user = self._get_by_id(user_data.id)
        if db_user.role != user_data.role and user.role != UserRole.ADMIN:
            self.raise_401_with_text("Only admin can do this")
        if db_user.username != user_data.username:
            self.raise_401_with_text("You can't do that")
        for field, value in user_data:
            setattr(db_user, field, value)
        try:
            self.session.commit()
        except Exception:
            self.raise_401_with_text("Fuck you!")
        return user_data

    def change_role(self, user: User, user_id: int, role: UserRole, replace: bool):
        db_user = self._get_by_id(user_id)
        if Roles.compare_role(db_user.role, role):
            raise self.raise_401_with_text("You not allowed to do that")
        if not Roles.compare_role(user.role, UserRole.ADMIN):
            raise self.raise_401_with_text("You not allowed to do that")
        else:
            if replace or role == UserRole.BANNED:
                db_user.role = role
            else:
                db_user.role = Roles.add_role(db_user.role, role)
        self.session.commit()
        return db_user