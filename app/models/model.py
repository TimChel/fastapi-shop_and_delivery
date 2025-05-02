from sqlmodel import SQLModel, Field
from pydantic import EmailStr


class UserBase(SQLModel):
    user_name: str = Field(description="Имя пользователя", max_length=30)
    email: EmailStr

class OrderBase(SQLModel):
    pass

class ProductBase(SQLModel):
    pass

class TruckBase(SQLModel):
    pass

class DeliveryBase(SQLModel):
    pass