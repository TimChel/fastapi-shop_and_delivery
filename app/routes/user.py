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


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=model.UserGetByAdmin, summary="Создать нового пользователя вручную")
def create_user(user: Annotated[model.UserCreateByAdmin, request_examples.exampl_create_user], session: Session = Depends(get_session)):
    new_user = add_user_to_db(user, session)
    return new_user