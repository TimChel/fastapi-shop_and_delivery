from fastapi import APIRouter, status, Depends, HTTPException
from app.models import model
from sqlmodel import Session, select
from app.auth import auth_handler
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation


def add_to_db(data, session):
    session.add(data)
    session.commit()
    session.refresh(data)
    return data

def add_user_to_db(user, access_level_name, session):
    access_level_name_check(access_level_name, session)
    extra_data = {"hashed_password": auth_handler.get_password_hash(user.password), "access_level_name": access_level_name}
    new_user = model.User.model_validate(user, update=extra_data)
    try:
        new_user = add_to_db(new_user, session)
        return new_user
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                           detail=f"Пользоатель с email {user.email} уже существует")

def update_user(db_user, user, session):
    try:
        db_user.sqlmodel_update(user.model_dump(exclude_unset=True))
        access_level_name_check(db_user.access_level_name, session)
        db_user = add_to_db(db_user, session)
        return db_user
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                           detail=f"Пользоатель с email {user.email} уже существует")


def access_level_name_check(access_level_name, session):
    access_level = session.exec(select(model.AccessLevel).where(model.AccessLevel.name == access_level_name)).first()
    if not access_level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Не существует уровня доступа с именем '{access_level_name}'")
    return access_level