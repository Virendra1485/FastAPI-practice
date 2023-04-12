from fastapi.testclient import TestClient


def test_read_main(client: TestClient):
    response = client.get("/v1/test_router")
    assert response.status_code == 200
    assert response.json() == {"hello": "hello"}


def test_user_sign_up(client: TestClient):
    response = client.post(
        "/v1/user/sign_up", json={"email": "test@gmail.com", "password": "Test@123"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@gmail.com"


def test_user_sign_in(client: TestClient, create_test_user):
    response = client.post(
        "/v1/user/sign_in", json={"email": "test@gmail.com", "password": "Test@123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_get_all_items(client: TestClient, get_auth_token: dict):
    response = client.get("/v1/items", headers=get_auth_token)
    assert response.status_code == 200
    assert response.json() == []


def test_create_item(client: TestClient, get_auth_token: dict):
    response = client.post(
        "/v1/items",
        json={"title": "testing", "description": "test_desc"},
        headers=get_auth_token,
    )
    assert response.status_code == 201
    assert response.json()["title"] == "testing"
