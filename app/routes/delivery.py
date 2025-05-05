from typing import Annotated
from fastapi import APIRouter, status, Depends, HTTPException
from app.models import model
from app.data_handler import (create_and_add_delivery_to_db, delete_delivery)
from app.db import get_session
from sqlmodel import Session, select
from app.auth import auth_handler


router = APIRouter(prefix="/delivery", tags=["Работа с перевозками"])


@router.get("/get/{delivery_id}", status_code=status.HTTP_200_OK, response_model=model.DeliveryWithOrderAndTruckGet)
def get_delivery_by_id(delivery_id: int, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    db_delivery = session.get(model.Delivery, delivery_id)
    if not db_delivery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Перевозки с id {delivery_id} не существет")
    if current_user.access_level.name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Данная информация доступна только пользователям с уровнем доступа 'admin'")
    return db_delivery

@router.get("/get", status_code=status.HTTP_200_OK, response_model=list[model.DeliveryWithOrderAndTruckGet])
def get_delivery_list(current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    if current_user.access_level.name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Данная информация доступна только пользователям с уровнем доступа 'admin'")
    db_delivery = session.exec(select(model.Delivery)).all()
    if not db_delivery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"В системе не зарегистрировано ни одной перевозки")
    return db_delivery

@router.get("/create", status_code=status.HTTP_201_CREATED, response_model=model.DeliveryWithOrderAndTruckGet, summary="Создать новую перевозку")
def create_delivery(current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    if current_user.access_level.name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Данная информация доступна только пользователям с уровнем доступа 'admin'")
    new_delivery = create_and_add_delivery_to_db(session)
    return new_delivery

@router.delete("/delete/{delivery_id}", status_code=status.HTTP_200_OK)
def delete_delivery_by_id(delivery_id: int, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    db_delivery = session.get(model.Delivery, delivery_id)
    if not db_delivery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Заказа с id {delivery_id} не существет")
    delete_delivery(db_delivery, session)
    return f"Перевозка отменена"