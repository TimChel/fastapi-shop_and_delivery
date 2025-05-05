from fastapi.testclient import TestClient
import faker
from app.main import app

client = TestClient(app)
fake = faker.Faker()

client.fake_user_email_1 = fake.email()
client.fake_user_password_1 = fake.password()
client.fake_user_name_1 = fake.first_name()
client.new_user_id = 0
client.auth_token = ""

client.fake_user_email_3 = fake.email()
client.fake_user_password_3 = fake.password()
client.fake_user_name_3 = fake.first_name()


client.fake_user_email_4 = fake.email()
client.fake_user_password_4 = fake.password()
client.fake_user_name_4 = fake.first_name()


def test_signup_admin():
    response = client.post("/auth/signup/admin",
                           json={"email": client.fake_user_email_1,
                                 "password": client.fake_user_password_1,
                                 "name": client.fake_user_name_1}
    )
    assert response.status_code == 201
    assert response.json()["access_level"]["name"] == "admin"
    client.new_user_id = response.json()["user_id"]

def test_signup_customer():
    response = client.post("/auth/signup/customer",
                           json={"email": client.fake_user_email_3,
                                 "password": client.fake_user_password_3,
                                 "name": client.fake_user_name_3}
    )
    assert response.status_code == 201
    assert response.json()["access_level"]["name"] == "customer"


def test_signup_provider():
    response = client.post("/auth/signup/provider",
                           json={"email": client.fake_user_email_4,
                                 "password": client.fake_user_password_4,
                                 "name": client.fake_user_name_4}
    )
    assert response.status_code == 201
    assert response.json()["access_level"]["name"] == "provider"

def test_login():
    response = client.post("/auth/login",
                           data={"username": client.fake_user_email_1,
                                 "password": client.fake_user_password_1}
    )
    assert response.status_code == 200
    client.auth_token = response.json()['access_token']


def test_me():
    response = client.get("/user/get/me", headers={"Authorization": f"Bearer {client.auth_token}"})
    assert response.status_code == 200
    assert response.json()["user_id"] == client.new_user_id