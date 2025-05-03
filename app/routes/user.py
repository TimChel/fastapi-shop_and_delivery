from typing import Annotated
from fastapi import APIRouter, status, Depends, HTTPException
from app.models import model
from app.api_docs import request_examples
from app.data_handler import (add_user_to_db, update_user)
from app.db import get_session
from sqlmodel import Session
from app.auth import auth_handler
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

router = APIRouter(prefix="/user", tags=["Работа с данными пользователей"])

@router.patch("/update/me", status_code=status.HTTP_200_OK, response_model=model.UserGet)
def update_user_by_admin(user: model.UserUpdate, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    updated_user = update_user(current_user, user, session)
    return updated_user

@router.patch("/update/admin/{user_id}", status_code=status.HTTP_200_OK, response_model=model.UserGetByAdmin)
def update_user_by_admin(user_id: int, user: model.UserUpdateByAdmin, session: Session = Depends(get_session)):
    db_user = session.get(model.User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Пользователя с id {user_id} не существет")
    updated_user = update_user(db_user, user, session)
    return updated_user

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=model.UserGetByAdmin, summary="Создать нового пользователя вручную")
def create_user_by_admin(user: Annotated[model.UserCreateByAdmin, request_examples.exampl_create_user], session: Session = Depends(get_session)):
    access_level_name = user.access_level_name
    new_user = add_user_to_db(user, access_level_name, session)
    return new_user

@router.post("/signup/admin", status_code=status.HTTP_201_CREATED, response_model=model.UserGet, summary="Зарегестрировать нового пользователя (алминистратор)")
def create_admin(user: model.UserCreate, session: Session = Depends(get_session)):
    access_level_name = "admin"
    new_user = add_user_to_db(user, access_level_name, session)
    return new_user

@router.post("/signup/customer", status_code=status.HTTP_201_CREATED, response_model=model.UserGet, summary="Зарегестрировать нового пользователя (покупатель)")
def create_customer(user: model.UserCreate, session: Session = Depends(get_session)):
    access_level_name = "customer"
    new_user = add_user_to_db(user, access_level_name, session)
    return new_user

@router.post("/signup/provider", status_code=status.HTTP_201_CREATED, response_model=model.UserGet, summary="Зарегестрировать нового пользователя (поставщик)")
def create_provider(user: model.UserCreate, session: Session = Depends(get_session)):
    access_level_name = "provider"
    new_user = add_user_to_db(user, access_level_name, session)
    return new_user





