from typing import Annotated
from fastapi import APIRouter, status, Depends, HTTPException
from app.models import model
from app.api_docs import request_examples
from app.data_handler import (add_product_to_db, update_product_p, delete_data)
from app.db import get_session
from sqlmodel import Session, select
from app.auth import auth_handler
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

router = APIRouter(prefix="/product", tags=["Работа с товарами"])

@router.get("/get/me", status_code=status.HTTP_200_OK, response_model=list[model.ProductWithProviderGet])
def get_product(current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    if current_user.access_level.name not in ('admin', 'provider'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Для использования данной функции необходимо иметь уровень доступа 'provider'/'admin'")
    if not current_user.products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Вы не зарегистрировали ни одного товара")
    return current_user.products

@router.get("/get/{id_product}", status_code=status.HTTP_200_OK, response_model=model.ProductWithProviderGet)
def get_product_by_id(id_product: int, session: Session = Depends(get_session)):
    db_product = session.get(model.Product, id_product)
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Товара с id {id_product} не существет")
    return db_product

@router.get("/get", status_code=status.HTTP_200_OK, response_model=list[model.ProductWithProviderGet])
def get_product_list(session: Session = Depends(get_session)):
    db_product = session.exec(select(model.Product)).all()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"В системе не зарегистрировано ни одного товара")
    return db_product

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=model.ProductWithProviderGet, summary="Создать новый продукт")
def create_product(product: model.ProductCreate, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    if current_user.access_level.name not in ('admin', 'provider'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Для использования данной функции необходимо иметь уровень доступа 'provider'/'admin'")
    new_product = add_product_to_db(product, current_user, session)
    return new_product

@router.patch("/update/{id_product}", status_code=status.HTTP_200_OK, response_model=model.ProductWithProviderGet)
def update_user(id_product: int, product: model.ProductUpdate, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    db_product = session.get(model.Product, id_product)
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Товара с id {id_product} не существет")
    if current_user.access_level.name != "admin" and db_product.provider.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Изменение товара другого пользователя запрещено ")
    updated_product = update_product_p(db_product, product, session)
    return updated_product

@router.delete("/delete/{id_product}", status_code=status.HTTP_200_OK)
def delete_product_by_id(id_product: int, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    db_product = session.get(model.Product, id_product)
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Товара с id {id_product} не существет")
    if current_user.access_level.name != "admin" and db_product.provider.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Удаление товара другого пользователя запрещено")
    db_product = delete_data(db_product, session)
    return f"Товар {db_product.name} удален"