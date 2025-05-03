from typing import Annotated
from fastapi import APIRouter, status, Depends, HTTPException
from app.models import model
from app.api_docs import request_examples
from app.data_handler import (add_truck_to_db)
from app.db import get_session
from sqlmodel import Session, select
from app.auth import auth_handler
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

router = APIRouter(prefix="/truck", tags=["Работа с автопарком"])


@router.get("/get/{truck_id}", status_code=status.HTTP_200_OK,  response_model=model.TruckGet)
def get_truck_by_id(truck_id: int, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    if current_user.access_level.name != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Для использования данной функции необходимо иметь уровень доступа 'admin'")
    db_truck = session.get(model.Truck, truck_id)
    if not db_truck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Грузовика с id {truck_id} не существет")
    return db_truck

@router.get("/get", status_code=status.HTTP_200_OK, response_model=list[model.TruckGet])
def get_truck_list(current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    if current_user.access_level.name != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Для использования данной функции необходимо иметь уровень доступа 'admin'")
    db_truck = session.exec(select(model.Truck)).all()
    if not db_truck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"В системе не зарегистрировано ни одного грузовика")
    return db_truck

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=model.TruckGet, summary="Добавить новый грузовик")
def create_truck(truck: model.TruckCreate, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
    if current_user.access_level.name != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Для использования данной функции необходимо иметь уровень доступа 'admin'")
    new_truck = add_truck_to_db(truck, session)
    return new_truck
#
# @router.patch("/update/{id_product}", status_code=status.HTTP_200_OK, response_model=model.ProductWithProviderGet)
# def update_user(id_product: int, product: model.ProductUpdate, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
#     db_product = session.get(model.Product, id_product)
#     if not db_product:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Товара с id {id_product} не существет")
#     if current_user.access_level.name != "admin" and db_product.provider.user_id != current_user.user_id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
#                             detail=f"Изменение товара другого пользователя запрещено ")
#     updated_product = update_product_p(db_product, product, session)
#     return updated_product
#
# @router.delete("/delete/{id_product}", status_code=status.HTTP_200_OK)
# def delete_product_by_id(id_product: int, current_user: Annotated[model.User, Depends(auth_handler.get_current_user)], session: Session = Depends(get_session)):
#     db_product = session.get(model.Product, id_product)
#     if not db_product:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Товара с id {id_product} не существет")
#     if current_user.access_level.name != "admin" and db_product.provider.user_id != current_user.user_id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
#                             detail=f"Удаление товара другого пользователя запрещено")
#     db_product = delete_data(db_product, session)
#     return f"Товар {db_product.name} удален"