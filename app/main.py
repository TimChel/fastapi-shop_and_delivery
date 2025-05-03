from fastapi import FastAPI
from sqlmodel import Session

from app.models.model import AccessLevel
from app.routes import (auth, delivery, order, product, truck, user)
from app.db import (init_database, engine)

def lifespan(app: FastAPI):
    init_database()
    with Session(engine) as session:
        access_level_1 = AccessLevel(name= "customer")
        access_level_2 = AccessLevel(name= "provider")
        access_level_3 = AccessLevel(name= "admin")
        session.add(access_level_1)
        session.add(access_level_2)
        session.add(access_level_3)
        session.commit()
    yield

app = FastAPI(
    # lifespan=lifespan,
    title="Система управления покупками и перевозками",
    description="Простейшая система управления покупками и перевозками, основанная на "
                "фреймворке FastAPI.",
    version="0.0.1",
    contact={
        "name": "Тимофей Челядинский",
        "url": "https://mipt.ru",
        "email": "cheliadinskii.tr@phystech.edu",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)

app.include_router(auth.router)
# app.include_router(delivery.router)
# app.include_router(order.router)
app.include_router(product.router)
# app.include_router(truck.router)
app.include_router(user.router)
