from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from sqlalchemy import UniqueConstraint

class UserBase(SQLModel):
    __table_args__ = (UniqueConstraint("email"),)
    name: str = Field(description="Имя пользователя", max_length=30)
    email: EmailStr = Field(unique_items=True, index=True)

class UserCreate(UserBase):
    password: str

class UserGet(UserBase):
    user_id: int

class UserWithAccessLevelGet(UserGet):
    access_level: "AccessLevelGet"

class UserCreateByAdmin(UserCreate):
    access_level_name: str = "customer"

class UserUpdate(SQLModel):
    name: str | None = Field(default= None, description="Имя пользователя", max_length=30)
    email: EmailStr | None = None

class UserUpdateByAdmin(UserUpdate):
    access_level_name: str | None = None

class User(UserBase, table=True):
    user_id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    access_level_id: int = Field(foreign_key="accesslevel.access_level_id")
    access_level: "AccessLevel" = Relationship(back_populates="users")
    products: list["Product"] = Relationship(back_populates="provider")
    # order: list["Order"]



class OrderBase(SQLModel):
    pass

# class Order(SQLModel, table=True):
#     order_id: int




class ProductBase(SQLModel):
    __table_args__ = (UniqueConstraint("name"),)
    name: str = Field(unique_items=True, index=True)
    size_x: int
    size_y: int

class ProductCreate(ProductBase):
    pass

class ProductGet(ProductBase):
    id_product: int

class ProductWithProviderGet(ProductGet):
    provider: "UserGet"

class ProductUpdate(SQLModel):
    name: str | None = None
    size_x: int | None = None
    size_y: int | None = None

class Product(ProductBase, table=True):
    id_product: int | None = Field(default=None, primary_key=True)
    provider: "User" = Relationship(back_populates="products")
    provider_id: int = Field(foreign_key="user.user_id")



class TruckBase(SQLModel):
    pass

class DeliveryBase(SQLModel):
    pass

class AccessLevelBase(SQLModel):
    __table_args__ = (UniqueConstraint("name"),)
    name: str = Field(unique_items=True, index=True)

class AccessLevelGet(AccessLevelBase):
    access_level_id: int

class AccessLevelWithUsersGet(AccessLevelGet):
    users: list["UserGet"]

class AccessLevel(AccessLevelBase, table=True):
    access_level_id: int | None = Field(default=None, primary_key=True)
    users: list["User"] = Relationship(back_populates="access_level")

