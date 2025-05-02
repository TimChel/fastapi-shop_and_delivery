from fastapi import APIRouter, status, Depends, HTTPExeption
from .models import model
from sqlmodel import Session
from .auth import auth_handler
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

def add_to_db(data, session):
    session.add(data)
    session.commit()
    session.refresh(data)
    return data

def add_user_to_db(user, session):
    extra_data = {"hash_password": auth_handler.get_password_hash(user.password)}
    new_user = model.User.model_validate(user, update=extra_data)
    try:
        new_user = add_to_db(new_user)
        return new_user
    except IntegrityError as e:
        assert isinstance(e.orig, UniqueViolation)
        raise HTTPExeption(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                           detail=f"Пользоатель с email {user.email} уже существует")