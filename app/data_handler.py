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

def delete_data(data, session):
    session.delete(data)
    session.commit()
    return data

def add_user_to_db(user, access_level_name, session):
    access_level = get_access_level(access_level_name, session)
    extra_data = {"hashed_password": auth_handler.get_password_hash(user.password), "access_level_id": access_level.access_level_id}
    new_user = model.User.model_validate(user, update=extra_data)
    try:
        new_user = add_to_db(new_user, session)
        return new_user
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                           detail=f"Пользоатель с email {user.email} уже существует")

def update_user_u(db_user, user, session):
    try:
        user_data = user.model_dump(exclude_unset=True)
        extra_data = {}
        if "access_level_name" in user_data:
            access_level = get_access_level(user.access_level_name, session)
            extra_data["access_level"] = access_level
        db_user.sqlmodel_update(user_data, update=extra_data)
        db_user = add_to_db(db_user, session)
        return db_user
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                           detail=f"Пользоатель с email {user.email} уже существует")


def get_access_level(access_level_name, session):
    access_level = session.exec(select(model.AccessLevel).where(model.AccessLevel.name == access_level_name)).first()
    if not access_level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Не существует уровня доступа с именем '{access_level_name}'")
    return access_level

def add_product_to_db(product, current_user, session):
    if product.size_x <=0 or product.size_y <= 0:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail=f"Размеры товар должны быть натуральными числами")
    extra_data = {"provider_id": current_user.user_id}
    new_product = model.Product.model_validate(product, update=extra_data)
    try:
        new_product = add_to_db(new_product, session)
        return new_product
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                           detail=f"Товар с названием '{product.name}' уже существует")

def update_product_p(db_product, product, session):
    try:
        product_data = product.model_dump(exclude_unset=True)
        db_product.sqlmodel_update(product_data)
        if db_product.size_x <= 0 or db_product.size_y <= 0:
            raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED,
                                detail=f"Размеры товар должны быть натуральными числами")
        db_product = add_to_db(db_product, session)
        return db_product
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                           detail=f"Товар с названием '{product.name}' уже существует")

def add_truck_to_db(truck, session):
    if truck.size_x <=0 or truck.size_y <= 0:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail=f"Размеры грузовика должны быть натуральными числами")
    new_truck = model.Truck.model_validate(truck)
    new_truck = add_to_db(new_truck, session)
    return new_truck

def add_order_to_db(order, current_user, session):
    product = session.get(model.Product, order.product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Товара с id {order.product_id} не существет")
    extra_data = {"user_id": current_user.user_id}
    new_order = model.Order.model_validate(order, update=extra_data)
    new_order = add_to_db(new_order, session)
    return new_order







