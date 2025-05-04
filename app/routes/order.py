from typing import Annotated
from fastapi import APIRouter, status, Depends, HTTPException
from app.models import model
from app.api_docs import request_examples
from app.data_handler import (add_order_to_db, delete_data)
from app.db import get_session
from sqlmodel import Session, select
from app.auth import auth_handler
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

router = APIRouter(prefix="/order", tags=["Работа с заказами"])

@router.get("/get/me", status_code=status.HTTP_200_OK, response_model=list[model.OrderWithProductAndUserGet])
def get_order(current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    if not current_user.orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Вы не инициировали ни одного заказа")
    return current_user.orders

@router.get("/get/{order_id}", status_code=status.HTTP_200_OK, response_model=model.OrderWithProductAndUserGet)
def get_order_by_id(order_id: int, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    db_order = session.get(model.Order, order_id)
    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Заказа с id {order_id} не существет")
    if current_user.access_level.name != "admin" and db_order.user.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Получение информации о заказе другого пользователя запрещено")
    return db_order

@router.get("/get", status_code=status.HTTP_200_OK, response_model=list[model.OrderWithProductAndUserGet])
def get_product_list(current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    if current_user.access_level.name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Данная информация доступна только пользователям с уровнем доступа 'admin'")
    db_order = session.exec(select(model.Order)).all()
    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"В системе не зарегистрировано ни одного товара")
    return db_order

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=model.OrderWithProductAndUserGet, summary="Создать новый заказ")
def create_order(order: model.OrderCreate, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    new_order = add_order_to_db(order, current_user, session)
    return new_order

@router.delete("/delete/{order_id}", status_code=status.HTTP_200_OK)
def delete_order_by_id(order_id: int, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    db_order = session.get(model.Order, order_id)
    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Заказа с id {order_id} не существет")
    if current_user.access_level.name != "admin" and db_order.user.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Удаление товара другого пользователя запрещено")
    if db_order.delivery_id is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Невозможно отменить заказ, который находтся в процессе доставки")
    db_order = delete_data(db_order, session)
    return f"Товар удален"