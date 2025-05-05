from typing import Annotated
from fastapi import APIRouter, status, Depends, HTTPException
from app.models import model
from app.data_handler import (add_truck_to_db, delete_data)
from app.db import get_session
from sqlmodel import Session, select
from app.auth import auth_handler


router = APIRouter(prefix="/truck", tags=["Работа с автопарком"])


@router.get("/get/{truck_id}", status_code=status.HTTP_200_OK,  response_model=model.TruckWithDeliveryAndOrderGet)
def get_truck_by_id(truck_id: int, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    if current_user.access_level.name != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Для использования данной функции необходимо иметь уровень доступа 'admin'")
    db_truck = session.get(model.Truck, truck_id)
    if not db_truck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Грузовика с id {truck_id} не существет")
    return db_truck

@router.get("/get", status_code=status.HTTP_200_OK, response_model=list[model.TruckWithDeliveryAndOrderGet])
def get_truck_list(current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    if current_user.access_level.name != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Для использования данной функции необходимо иметь уровень доступа 'admin'")
    db_truck = session.exec(select(model.Truck)).all()
    if not db_truck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"В системе не зарегистрировано ни одного грузовика")
    return db_truck

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=model.TruckWithDeliveryAndOrderGet, summary="Добавить новый грузовик")
def create_truck(truck: model.TruckCreate, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    if current_user.access_level.name != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Для использования данной функции необходимо иметь уровень доступа 'admin'")
    new_truck = add_truck_to_db(truck, session)
    return new_truck

@router.delete("/delete/{truck_id}", status_code=status.HTTP_200_OK)
def delete_truck_by_id(truck_id: int, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    db_truck = session.get(model.Truck, truck_id)
    if not db_truck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Грузовика с id {truck_id} не существет")
    if current_user.access_level.name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Удаление грузовика запрещено")
    if db_truck.delivery_id is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Невозможно отменить грузовик, который находтся в процессе доставки")
    delete_data(db_truck, session)
    return f"Грузовик удален"