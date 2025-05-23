from datetime import timedelta
from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import Session, select
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.data_handler import (add_user_to_db)
from app.db import get_session
from app.models import model
from app.auth import auth_handler
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Безопасность"])

@router.post("/signup/admin", status_code=status.HTTP_201_CREATED, response_model=model.UserWithAccessLevelOrderProductGet, summary="Зарегестрировать нового пользователя (алминистратор)")
def create_admin(user: model.UserCreate, session: Session = Depends(get_session)):
    access_level_name = "admin"
    new_user = add_user_to_db(user, access_level_name, session)
    return new_user

@router.post("/signup/customer", status_code=status.HTTP_201_CREATED, response_model=model.UserWithAccessLevelOrderProductGet, summary="Зарегестрировать нового пользователя (покупатель)")
def create_customer(user: model.UserCreate, session: Session = Depends(get_session)):
    access_level_name = "customer"
    new_user = add_user_to_db(user, access_level_name, session)
    return new_user

@router.post("/signup/provider", status_code=status.HTTP_201_CREATED, response_model=model.UserWithAccessLevelOrderProductGet, summary="Зарегестрировать нового пользователя (поставщик)")
def create_provider(user: model.UserCreate, session: Session = Depends(get_session)):
    access_level_name = "provider"
    new_user = add_user_to_db(user, access_level_name, session)
    return new_user

@router.post("/login", status_code=status.HTTP_200_OK,
             summary = 'Войти в систему')
def user_login(login_attempt_data: OAuth2PasswordRequestForm = Depends(),
               session: Session = Depends(get_session)):
    statement = (select(model.User)
                 .where(model.User.email == login_attempt_data.username))
    existing_user = session.exec(statement).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Пользователя с email '{login_attempt_data.username}' не существует"
        )

    if auth_handler.verify_password(
            login_attempt_data.password,
            existing_user.hashed_password):
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = auth_handler.create_access_token(
            data={"sub": login_attempt_data.username},
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Введен неверный пароль для пользоателя '{login_attempt_data.username}'"
        )
