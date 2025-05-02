from email.policy import default
from operator import index

from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from sqlalchemy import UniqueConstraint


class UserBase(SQLModel):
    __table_args__ = (UniqueConstraint("email"),)
    name: str = Field(description="Имя пользователя", max_length=30)
    email: EmailStr = Field(unique_items=True, index=True)

class UserCreateByAdmin(UserBase):
    access_level_name: str

class User(UserBase, table=True):
    user_id: int | None = Field(default=None, primary_key=True)
    access_level: "AccessLevel"
    hashed_password: str
    order: list["Order"]

class OrderBase(SQLModel):
    pass

class Order(SQLModel, table=True):
    pass

class ProductBase(SQLModel):
    pass

class TruckBase(SQLModel):
    pass

class DeliveryBase(SQLModel):
    pass

class AccessLevel(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("name"),)
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique_items=True, index=True)