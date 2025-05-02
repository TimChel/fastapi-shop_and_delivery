from typing import Annotated
from fastapi import APIRouter, status, Depends, HTTPExeption
from ..models import model
from ..api_docs import request_examples
from app.data_handler import (add_user_to_db)
from app.db import get_session
from sqlmodel import Session
from ..auth import auth_handler

router = APIRouter(prefix="/user", tags=("Работа с данными пользователей"))


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=model.UserCreate, summary="Создать нового пользователя вручную")
def create_user(user: Annotated[model.UserCreate, request_examples.exampl_create_user], session: Session = Depends(get_session)):
    extra_data = auth_handler.
    new_user = model.User.model_validate(user, update=extra_data)
    new_user = add_user_to_db(user)