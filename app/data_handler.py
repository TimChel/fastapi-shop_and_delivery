from os import access

from fastapi import APIRouter, status, Depends, HTTPException
from .models import model
from sqlmodel import Session, select
from .auth import auth_handler
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from .models.model import AccessLevel


def add_to_db(data, session):
    session.add(data)
    session.commit()
    session.refresh(data)
    return data

def add_user_to_db(user, access_level_name, session):
    access_level = session.exec(select(AccessLevel).where(AccessLevel.name == access_level_name)).first()
    if not access_level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Не существует уровня доступа с именем '{access_level_name}'")
    extra_data = {"hashed_password": auth_handler.get_password_hash(user.password), "access_level": access_level}
    new_user = model.User.model_validate(user, update=extra_data)
    try:
        new_user = add_to_db(new_user, session)
        return new_user
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                           detail=f"Пользоатель с email {user.email} уже существует")