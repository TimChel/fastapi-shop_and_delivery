from typing import Annotated, Depends
from fastapi import APIRouter, status
from ..models import model
from ..api_docs import request_examples
from app.data_handler import (add_user_to_db)
from app.db import get_session
from sqlmodel import Session

router = APIRouter(prefix="/user", tags=("Работа с данными пользователей"))


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=model.UserCreate, summary="Создать нового пользователя вручную")
def create_user(user: Annotated[model.UserCreate, request_examples.exampl_create_user], session: Session = Depends(get_session)):
    new_user = 
    new_user = add_user_to_db(user)