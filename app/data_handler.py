from operator import index

from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from app.models import model
from app.auth import auth_handler
from app.models.model import Delivery
from app.sort_test.truck_sort import *


def add_to_db(data, session):
    session.add(data)
    session.commit()
    session.refresh(data)
    return data

def delete_data(data, session):
    session.delete(data)
    session.commit()
    return data

def size_check(size_x, size_y, turn_permission, session):
    if size_x <=0 or size_y <= 0:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED,
                            detail="Размеры товар должны быть натуральными числами")
    for truck in session.exec(select(model.Truck)).all():
        if size_x <= truck.size_x and size_y <= truck.size_y:
            return True
        if turn_permission and size_y <= truck.size_x and size_x <= truck.size_y:
            return True
    raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED,
                        detail="К сожалению, у нас нет грузовика,"
                               " в который поместился бы ваш товар."
                               " Приносим свою извинения")

def add_user_to_db(user, access_level_name, session):
    access_level = get_access_level(access_level_name, session)
    extra_data = {"hashed_password": auth_handler.get_password_hash(user.password),
                  "access_level_id": access_level.access_level_id}
    new_user = model.User.model_validate(user, update=extra_data)
    try:
        new_user = add_to_db(new_user, session)
        return new_user
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                           detail=f"Пользоатель с email {user.email} уже существует")

def update_user_u(db_user, user, session):
    try:
        user_data = user.model_dump(exclude_unset=True)
        extra_data = {}
        if "access_level_name" in user_data:
            access_level = get_access_level(user_data["access_level_name"], session)
            extra_data["access_level_id"] = access_level.access_level_id
        db_user.sqlmodel_update(user_data, update=extra_data)
        db_user = add_to_db(db_user, session)
        return db_user
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                           detail=f"Пользоатель с email {user.email} уже существует")


def get_access_level(access_level_name, session):
    access_level = (
        session.exec(select(model.AccessLevel).where(model.AccessLevel.name
                                                     == access_level_name)).first())
    if not access_level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Не существует"
                                   f" уровня доступа с именем '{access_level_name}'")
    return access_level

def add_product_to_db(product, current_user, session):
    extra_data = {"provider_id": current_user.user_id}
    new_product = model.Product.model_validate(product, update=extra_data)
    size_check(new_product.size_x, new_product.size_y, new_product.turn_permission, session)
    try:
        new_product = add_to_db(new_product, session)
        return new_product
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                           detail=f"Товар с названием '{product.name}' уже существует")

def update_product_p(db_product, product, session):
    try:
        product_data = product.model_dump(exclude_unset=True)
        db_product.sqlmodel_update(product_data)
        size_check(db_product.size_x, db_product.size_y, db_product.turn_permission, session)
        db_product = add_to_db(db_product, session)
        return db_product
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                           detail=f"Товар с названием '{product.name}' уже существует")

def add_truck_to_db(truck, session):
    if truck.size_x <=0 or truck.size_y <= 0:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED,
                            detail="Размеры грузовика должны быть натуральными числами")
    new_truck = model.Truck.model_validate(truck)
    new_truck = add_to_db(new_truck, session)
    return new_truck

def add_order_to_db(order, current_user, session):
    product = session.get(model.Product, order.product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Товара с id {order.product_id} не существет")
    extra_data = {"user_id": current_user.user_id}
    new_order = model.Order.model_validate(order, update=extra_data)
    new_order = add_to_db(new_order, session)
    return new_order

def create_and_add_delivery_to_db(session):
    order = session.exec(select(model.Order).where(model.Order.on_the_way == False)).all()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="На складе нет товаров, требуемых достаку")
    truck = session.exec(select(model.Truck).where(model.Truck.available==True)).all()
    if not truck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Нет доступных для перевозки грузовиков")
    truck_data = []
    order_data = []
    for i in truck:
        truck_data.append({
            "id": i.id,
            "free_space": [[x, y] for x in range(i.size_x) for y in range(i.size_y)],
            "order_id": [],
            "size": [i.size_x, i.size_y],
            "money": i.cost
        })
    for i in order:
        order_data.append({
            "id": i.id,
            "size": [[x, y] for x in range(i.product.size_x)
                     for y in range(i.product.size_y)],
            "turn_permission": i.product.turn_permission,
            "date": i.creation_date,
            "truck_id": -1
        })
    (non_empty_truck, order_in_truck, money) = truck_sort(truck_data, order_data)
    if not non_empty_truck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Нет доступных для перевозки грузовиков!!!")
    delivery = Delivery(cost=money)
    delivery = add_to_db(delivery, session)
    for i_truck in truck:
        index_list_non_empty_truck = [non_empty_truck[i]["id"] for i in range(len(non_empty_truck))]
        if non_empty_truck and i_truck.id in index_list_non_empty_truck:
            index_non_empty_truck = index_list_non_empty_truck.index(i_truck.id)
            i_truck.delivery_id = delivery.id
            i_truck.available = False
            add_to_db(i_truck, session)
            non_empty_truck.pop(index_non_empty_truck)
    for i_order in order:
        index_list_order_in_truck = [order_in_truck[i]["id"] for i in range(len(order_in_truck))]
        if order_in_truck and i_order.id in index_list_order_in_truck:
            index_order_in_truck = index_list_order_in_truck.index(i_order.id)
            i_order.truck_id = order_in_truck[index_order_in_truck]["truck_id"]
            i_order.delivery_id = delivery.id
            i_order.on_the_way = True
            add_to_db(i_order, session)
            order_in_truck.pop(index_order_in_truck)
    session.refresh(delivery)
    return delivery

def delete_delivery(delivery, session):
    for order in delivery.orders:
        order.on_the_way = False
        order.truck_id = None
        add_to_db(order, session)
    for truck in delivery.trucks:
        truck.available = True
    return delete_data(delivery, session)









