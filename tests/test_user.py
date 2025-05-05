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
client.new_user_email = fake.email()
client.new_user_password = fake.password()
client.new_user_name = fake.first_name()
client.new_access_level = random.choice(["admin", "customer", "provider"])
client.new_new_user_email = fake.email()
client.new_new_user_name = fake.first_name()
client.new_new_access_level = random.choice(["admin", "customer", "provider"])
client.new_user_id = 0

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

def test_new_user():
    response = client.post("/user/create",
                           json={"email": client.new_user_email,
                                 "password": client.new_user_password,
                                 "name": client.new_user_name,
                                 "access_level_name": client.new_access_level},
                           headers={"Authorization": f"Bearer {client.auth_token}"}
                           )
    assert response.status_code == 201
    client.new_user_id = response.json()["user_id"]

def test_get_new_user():
    response = client.get("/user/get/"+str(client.new_user_id),
                          headers={"Authorization": f"Bearer {client.auth_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == client.new_user_email

def test_update_new_user():
    response = client.patch("/user/update/admin/"+str(client.new_user_id),
                            headers={"Authorization": f"Bearer {client.auth_token}"},
                            json={"email": client.new_new_user_email,
                                  "name": client.new_new_user_name,
                                  "access_level_name": client.new_new_access_level},
                            )
    assert response.status_code == 200
    assert (response.json()["email"], response.json()["name"], response.json()["access_level"]["name"]) == (client.new_new_user_email, client.new_new_user_name, client.new_new_access_level)

def test_delete_new_user():
    response =client.delete("/user/delete/"+str(client.new_user_id),
                            headers={"Authorization": f"Bearer {client.auth_token}"},)
    assert response.status_code == 200

