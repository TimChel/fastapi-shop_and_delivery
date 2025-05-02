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


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=model.UserGet_by_Admin, summary="Создать нового пользователя вручную")
def create_user(user: Annotated[model.UserCreate, request_examples.exampl_create_user], session: Session = Depends(get_session)):
    extra_data = {"hash_password": auth_handler.get_password_hash(user.password)}
    new_user = model.User.model_validate(user, update=extra_data)
    try:
        new_user = add_user_to_db(new_user)
        # session.add(new_user)
        # session.commit()
        # session.refresh(new_user)
        return new_user
    except IntegrityError as e:
        assert isinstance(e.orig, UniqueViolation)
        raise HTTPExeption(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Пользоатель с email {user.email} уже существует")
    