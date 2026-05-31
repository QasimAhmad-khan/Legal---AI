from fastapi.testclient import TestClient
import io

def get_token(client: TestClient):
    client.post("/api/auth/register", json={"email": "doc@example.com", "password": "password", "role": "admin"})
    res = client.post("/api/auth/login", data={"username": "doc@example.com", "password": "password"})
    return res.json()["access_token"]

def test_invalid_file_type(client: TestClient):
    token = get_token(client)
    res = client.post("/api/documents", files={"file": ("test.png", b"fake png data", "image/png")}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 400

def test_valid_txt_upload(client: TestClient):
    token = get_token(client)
    res = client.post("/api/documents", files={"file": ("test.txt", b"This is a test contract.", "text/plain")}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["filename"] == "test.txt"
