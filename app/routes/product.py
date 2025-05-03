from typing import Annotated
from fastapi import APIRouter, status, Depends, HTTPException
from app.models import model
from app.api_docs import request_examples
from app.data_handler import (add_product_to_db)
from app.db import get_session
from sqlmodel import Session, select
from app.auth import auth_handler
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

router = APIRouter(prefix="/product", tags=["Работа с товарами"])

@router.get("/get/me", status_code=status.HTTP_200_OK, response_model=list[model.ProductGet])
def get_product(current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    return current_user.products
#
# @router.get("/get/{user_id}", status_code=status.HTTP_200_OK, response_model=model.UserWithAccessLevelGet)
# def get_user_by_id(user_id: int, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
#     if current_user.access_level.name != 'admin':
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Для использования данной функции необходимо иметь уровень доступа 'admin'")
#     db_user = session.get(model.User, user_id)
#     if not db_user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Пользователя с id {user_id} не существет")
#     return db_user
#
# @router.get("/get", status_code=status.HTTP_200_OK, response_model=list[model.UserWithAccessLevelGet])
# def get_user_list(current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
#     if current_user.access_level.name != 'admin':
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Для использования данной функции необходимо иметь уровень доступа 'admin'")
#     db_user = session.exec(select(model.User)).all()
#     if not db_user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"В системе не зарегистрировано ни одного пользователя")
#     return db_user
#
@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=model.ProductGet, summary="Создать новый продукт")
def create_product(product: model.ProductCreate, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    if current_user.access_level.name not in ('admin', 'provider'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Для использования данной функции необходимо иметь уровень доступа 'provider'/'admin'")
    new_product = add_product_to_db(product, current_user, session)
    return new_product
#
# @router.post("/signup/admin", status_code=status.HTTP_201_CREATED, response_model=model.UserWithAccessLevelGet, summary="Зарегестрировать нового пользователя (алминистратор)")
# def create_admin(user: model.UserCreate, session: Session = Depends(get_session)):
#     access_level_name = "admin"
#     new_user = add_user_to_db(user, access_level_name, session)
#     return new_user
#
# @router.post("/signup/customer", status_code=status.HTTP_201_CREATED, response_model=model.UserWithAccessLevelGet, summary="Зарегестрировать нового пользователя (покупатель)")
# def create_customer(user: model.UserCreate, session: Session = Depends(get_session)):
#     access_level_name = "customer"
#     new_user = add_user_to_db(user, access_level_name, session)
#     return new_user
#
# @router.post("/signup/provider", status_code=status.HTTP_201_CREATED, response_model=model.UserWithAccessLevelGet, summary="Зарегестрировать нового пользователя (поставщик)")
# def create_provider(user: model.UserCreate, session: Session = Depends(get_session)):
#     access_level_name = "provider"
#     new_user = add_user_to_db(user, access_level_name, session)
#     return new_user
#
# @router.patch("/update/me", status_code=status.HTTP_200_OK, response_model=model.UserWithAccessLevelGet)
# def update_user(user: model.UserUpdate, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
#     updated_user = update_user_u(current_user, user, session)
#     return updated_user
#
# @router.patch("/update/admin/{user_id}", status_code=status.HTTP_200_OK, response_model=model.UserWithAccessLevelGet)
# def update_user_by_admin(user_id: int, user: model.UserUpdateByAdmin, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
#     if current_user.access_level.name != 'admin':
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Для использования данной функции необходимо иметь уровень доступа 'admin'")
#     db_user = session.get(model.User, user_id)
#     if not db_user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Пользователя с id {user_id} не существет")
#     updated_user = update_user(db_user, user, session)
#     return updated_user
#
# @router.delete("/delete/{user_id}", status_code=status.HTTP_200_OK)
# def delete_user_by_id(user_id: int, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
#     if current_user.access_level.name != 'admin':
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Для использования данной функции необходимо иметь уровень доступа 'admin'")
#     if current_user.user_id == user_id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Удаление собственного аккаунта запрещено")
#     db_user = session.get(model.User, user_id)
#     if not db_user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Пользователя с id {user_id} не существет")
#     db_user = delete_data(db_user, session)
#     return f"Аккаунт {db_user.email} удален"