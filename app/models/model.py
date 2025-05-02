from sqlmodel import SQLModel, Field
from pydantic import EmailStr


class User(SQLModel):
    user_name: str = Field(description="Имя пользователя", max_length=30)
    email: EmailStr

class Order(SQLModel):
    pass

class Product(SQLModel):
    pass

class Truck(SQLModel):
    pass

class Delivery(SQLModel):
    pass