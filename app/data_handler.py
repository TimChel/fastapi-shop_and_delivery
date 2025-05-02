from os import access

from fastapi import APIRouter, status, Depends, HTTPExeption
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

def add_user_to_db(user, session):
    access_level = session.exec(select(AccessLevel).where(AccessLevel.name == user.access_level_name)).first()
    if not access_level:
        raise HTTPExeption(status_code=status.HTTP_404_NOT_FOUN, detail=f"Не существует уровня доступа с именем {user.access_level_name}")
    extra_data = {"hash_password": auth_handler.get_password_hash(user.password), "access_level": access_level}
    new_user = model.User.model_validate(user, update=extra_data)
    try:
        new_user = add_to_db(new_user, session)
        return new_user
    except IntegrityError as e:
        assert isinstance(e.orig, UniqueViolation)
        raise HTTPExeption(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                           detail=f"Пользоатель с email {user.email} уже существует")