from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from app.config import settings
from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from fastapi.security import OAuth2PasswordBearer
from app.db import get_session
from jwt.exceptions import InvalidTokenError
from app.models import model

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)

def create_access_token(data: dict,
                        expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = (datetime.now(timezone.utc) +
                  expires_delta)
    else:
        expire = (datetime.now(timezone.utc) +
                  timedelta(minutes=15))

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode,
                             settings.secret_key,
                             algorithm=settings.algo)
    return encoded_jwt

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                     session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algo])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    statement = (select(model.User)
                 .where(model.User.email == username))
    user = session.exec(statement).first()

    if user is None:
        raise credentials_exception
    return user