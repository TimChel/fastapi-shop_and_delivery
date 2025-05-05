from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from sqlalchemy import UniqueConstraint
from datetime import date

class UserBase(SQLModel):
    __table_args__ = (UniqueConstraint("email"),)
    name: str = Field(description="Имя пользователя")
    email: EmailStr = Field(unique_items=True, index=True)

class UserCreate(UserBase):
    password: str

class UserGet(UserBase):
    user_id: int

class UserWithAccessLevelOrderProductGet(UserGet):
    access_level: "AccessLevelGet"
    orders: list["OrderGet"]
    products: list["ProductGet"]

class UserCreateByAdmin(UserCreate):
    access_level_name: str = "customer"

class UserUpdate(SQLModel):
    name: str | None = Field(default= None, description="Имя пользователя",)
    email: EmailStr | None = None

class UserUpdateByAdmin(UserUpdate):
    access_level_name: str | None = None

class User(UserBase, table=True):
    user_id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    access_level_id: int = Field(foreign_key="accesslevel.access_level_id")
    access_level: "AccessLevel" = Relationship(back_populates="users")
    products: list["Product"] = Relationship(back_populates="provider", cascade_delete=True)
    orders: list["Order"] = Relationship(back_populates="user", cascade_delete=True)



class DeliveryBase(SQLModel):
    cost: int

class DeliveryGet(DeliveryBase):
    id: int

class DeliveryWithOrderAndTruckGet(DeliveryGet):
    orders: list["OrderGet"]
    trucks: list["TruckGet"]

class Delivery(DeliveryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    orders: list["Order"] = Relationship(back_populates="delivery")
    trucks: list["Truck"] = Relationship(back_populates="delivery")




class TruckBase(SQLModel):
    size_x: int
    size_y: int
    cost: int

class TruckGet(TruckBase):
    id: int
    available: bool

class TruckWithDeliveryAndOrderGet(TruckGet):
    delivery: DeliveryGet | None
    orders: list["Order"]

class TruckCreate(TruckBase):
    pass

class Truck(TruckBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    available: bool = True
    delivery_id: int | None = Field(default=None, foreign_key="delivery.id")
    delivery: Delivery | None = Relationship(back_populates="trucks")
    orders: list["Order"] = Relationship(back_populates="truck")





class OrderBase(SQLModel):
    creation_date: date = Field(default=date.today())

class OrderGet(OrderBase):
    id: int

class OrderWithProductAndUserAndDeliveryAnTruckGet(OrderGet):
    product: "ProductGet"
    user: "UserGet"
    delivery: DeliveryGet | None
    on_the_way: bool
    truck: TruckGet | None

class OrderCreate(SQLModel):
    product_id: int

class Order(OrderBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id_product")
    product: "Product" = Relationship(back_populates="orders")
    user_id: int = Field(foreign_key="user.user_id")
    user: "User" = Relationship(back_populates="orders")
    delivery_id: int | None = Field(default=None, foreign_key="delivery.id")
    delivery: Delivery | None = Relationship(back_populates="orders")
    on_the_way: bool = False
    truck_id: int | None = Field(default=None, foreign_key="truck.id")
    truck: Truck | None = Relationship(back_populates="orders")





class ProductBase(SQLModel):
    __table_args__ = (UniqueConstraint("name"),)
    name: str = Field(unique_items=True, index=True)
    size_x: int
    size_y: int
    turn_permission: bool = True

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
    turn_permission: bool | None = None

class Product(ProductBase, table=True):
    id_product: int | None = Field(default=None, primary_key=True)
    provider: "User" = Relationship(back_populates="products")
    provider_id: int = Field(foreign_key="user.user_id")
    orders: list["Order"] = Relationship(back_populates="product", cascade_delete=True)





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

