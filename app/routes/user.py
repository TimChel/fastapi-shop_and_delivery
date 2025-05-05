from typing import Annotated
from fastapi import APIRouter, status, Depends, HTTPException
from app.models import model
from app.data_handler import (add_user_to_db, update_user_u, delete_data)
from app.db import get_session
from sqlmodel import Session, select
from app.auth import auth_handler


router = APIRouter(prefix="/user", tags=["Работа с данными пользователей"])

@router.get("/get/me", status_code=status.HTTP_200_OK, response_model=model.UserWithAccessLevelOrderProductGet)
def get_user(current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    return current_user

@router.get("/get/{user_id}", status_code=status.HTTP_200_OK, response_model=model.UserWithAccessLevelOrderProductGet)
def get_user_by_id(user_id: int, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    if current_user.access_level.name != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Для использования данной функции необходимо иметь уровень доступа 'admin'")
    db_user = session.get(model.User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Пользователя с id {user_id} не существет")
    return db_user

@router.get("/get", status_code=status.HTTP_200_OK, response_model=list[model.UserWithAccessLevelOrderProductGet])
def get_user_list(current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    if current_user.access_level.name != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Для использования данной функции необходимо иметь уровень доступа 'admin'")
    db_user = session.exec(select(model.User)).all()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"В системе не зарегистрировано ни одного пользователя")
    return db_user

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=model.UserWithAccessLevelOrderProductGet, summary="Создать нового пользователя вручную")
def create_user_by_admin(user: model.UserCreateByAdmin, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    if current_user.access_level.name != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Для использования данной функции необходимо иметь уровень доступа 'admin'")
    access_level_name = user.access_level_name
    new_user = add_user_to_db(user, access_level_name, session)
    return new_user

@router.patch("/update/me", status_code=status.HTTP_200_OK, response_model=model.UserWithAccessLevelOrderProductGet)
def update_user(user: model.UserUpdate, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    updated_user = update_user_u(current_user, user, session)
    return updated_user

@router.patch("/update/admin/{user_id}", status_code=status.HTTP_200_OK, response_model=model.UserWithAccessLevelOrderProductGet)
def update_user_by_admin(user_id: int, user: model.UserUpdateByAdmin, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    if current_user.access_level.name != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Для использования данной функции необходимо иметь уровень доступа 'admin'")
    db_user = session.get(model.User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Пользователя с id {user_id} не существет")
    updated_user = update_user_u(db_user, user, session)
    return updated_user

@router.delete("/delete/{user_id}", status_code=status.HTTP_200_OK)
def delete_user_by_id(user_id: int, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    if current_user.access_level.name != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Для использования данной функции необходимо иметь уровень доступа 'admin'")
    if current_user.user_id == user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Удаление собственного аккаунта запрещено")
    db_user = session.get(model.User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Пользователя с id {user_id} не существет")
    if any([i.on_the_way for i in db_user.orders]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Невозможно удалить пользователя, чей заказ находится в процессе доставки")
    if any([any([y.on_the_way for y in i.orders]) for i in db_user.products]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Невозможно удалить пользователя, чей товар находится в процессе доставки")
    db_user = delete_data(db_user, session)
    return f"Аккаунт {db_user.email} удален"






