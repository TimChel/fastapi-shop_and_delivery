from fastapi.testclient import TestClient
import faker
import random
from app.main import app

client = TestClient(app)
fake = faker.Faker()

client.fake_user_email = fake.email()
client.fake_user_password = fake.password()
client.fake_user_name = fake.first_name()
client.user_id = 0
client.auth_token = ""
client.truck_size_x = fake.pyint(1, 10)
client.truck_size_y = fake.pyint(1, 10)
client.truck_cost = fake.pyint(1)
client.product_name = fake.pystr()
client.product_size_x = fake.pyint(1, client.truck_size_x)
client.product_size_y = fake.pyint(1, client.truck_size_y)
client.product_turn_permission = fake.pybool()
client.product_id = 0
client.order_product_id = 0
client.order_id = 0
client.delivery_id = 0

def test_signup_admin():
    response = client.post("/auth/signup/admin",
                           json={"email": client.fake_user_email,
                                 "password": client.fake_user_password,
                                 "name": client.fake_user_name}
    )
    assert response.status_code == 201
    assert response.json()["access_level"]["name"] == "admin"
    client.user_id = response.json()["user_id"]

def test_login():
    response = client.post("/auth/login",
                           data={"username": client.fake_user_email,
                                 "password": client.fake_user_password}
    )
    assert response.status_code == 200
    client.auth_token = response.json()['access_token']

def test_truck_create():
    response = client.post("/truck/create",
                           json={"size_x": client.truck_size_x,
                                 "size_y": client.truck_size_y,
                                 "cost": client.truck_cost},
                           headers={"Authorization": f"Bearer {client.auth_token}"}
                           )
    assert response.status_code == 201
    assert (response.json()["size_x"], response.json()["size_y"], response.json()["cost"]) == (client.truck_size_x, client.truck_size_y, client.truck_cost)

def test_create_product():
    response = client.post("/product/create",
                           json={"name": client.product_name,
                                 "size_x": client.product_size_x,
                                 "size_y": client.product_size_y,
                                 "turn_permission": client.product_turn_permission},
                           headers={"Authorization": f"Bearer {client.auth_token}"}
                           )
    assert response.status_code == 201
    client.product_id = response.json()["id_product"]

def test_create_order():
    response = client.post("/order/create",
                           json={"product_id": client.product_id},
                           headers={"Authorization": f"Bearer {client.auth_token}"}
                           )
    assert response.status_code == 201
    client.order_id = response.json()["id"]

def test_create_delivery():
    response = client.get("/delivery/create",
                           headers={"Authorization": f"Bearer {client.auth_token}"}
                           )
    assert response.status_code == 201
    client.delivery_id = response.json()["id"]

def test_get_delivery():
    response = client.get("/delivery/get/"+str(client.delivery_id),
                          headers={"Authorization": f"Bearer {client.auth_token}"})
    assert response.status_code == 200
    assert response.json()["id"] == client.delivery_id

def test_delete_order():
    response = client.delete("/delivery/delete/"+str(client.delivery_id),
                            headers={"Authorization": f"Bearer {client.auth_token}"},)
    assert response.status_code == 200