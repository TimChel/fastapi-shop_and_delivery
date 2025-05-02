from typing import Annotated
from fastapi import APIRouter, status, Depends, HTTPExeption
from ..models import model
from ..api_docs import request_examples
from app.data_handler import (add_user_to_db)
from app.db import get_session
from sqlmodel import Session
from ..auth import auth_handler
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

router = APIRouter(prefix="/user", tags=("Работа с данными пользователей"))


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=model.UserGetByAdmin, summary="Создать нового пользователя вручную")
def create_user_by_admin(user: Annotated[model.UserCreateByAdmin, request_examples.exampl_create_user], session: Session = Depends(get_session)):
    new_user = add_user_to_db(user, session)
    return new_user

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=model.UserGet, summary="Зарегестрировать нового пользователя (алминистратор)")
def create_admin(user: Annotated[model.UserCreate, request_examples.exampl_create_user], session: Session = Depends(get_session)):
    new_user = add_user_to_db(user, session)
    return new_user

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=model.UserGet, summary="Зарегестрировать нового пользователя (покупатель)")
def create_customer(user: Annotated[model.UserCreate, request_examples.exampl_create_user], session: Session = Depends(get_session)):
    new_user = add_user_to_db(user, session)
    return new_user

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=model.UserGet, summary="Зарегестрировать нового пользователя (поставщик)")
def create_provider(user: Annotated[model.UserCreate, request_examples.exampl_create_user], session: Session = Depends(get_session)):
    new_user = add_user_to_db(user, session)
    return new_user

