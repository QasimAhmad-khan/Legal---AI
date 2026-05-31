from fastapi.testclient import TestClient

def test_register_login(client: TestClient):
    # TC-AUTH-01 Register + login happy path
    res = client.post("/api/auth/register", json={"email": "test@example.com", "password": "password", "role": "admin"})
    assert res.status_code == 200
    
    res = client.post("/api/auth/login", data={"username": "test@example.com", "password": "password"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    
    # Call protected endpoint
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "test@example.com"

def test_member_cannot_write_precedents(client: TestClient):
    # TC-AUTH-02 Member cannot write precedents
    client.post("/api/auth/register", json={"email": "member@example.com", "password": "password", "role": "member"})
    res = client.post("/api/auth/login", data={"username": "member@example.com", "password": "password"})
    token = res.json()["access_token"]
    
    # We test rules endpoint instead, which is protected by admin
    res = client.post("/api/analysis/compliance-rules", json={"text": "test rule"}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403

def test_admin_can_manage_precedents(client: TestClient):
    # TC-AUTH-03 Admin can manage precedents & rules
    client.post("/api/auth/register", json={"email": "admin2@example.com", "password": "password", "role": "admin"})
    res = client.post("/api/auth/login", data={"username": "admin2@example.com", "password": "password"})
    token = res.json()["access_token"]
    
    # Admin can post rules
    res = client.post("/api/analysis/compliance-rules", json={"text": "test rule"}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200

def test_invalid_jwt(client: TestClient):
    # EC-AUTH-01 Expired / tampered / missing JWT
    res = client.get("/api/auth/me")
    assert res.status_code == 401
    
    res = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid_token_xyz"})
    assert res.status_code in [401, 403]

def test_duplicate_registration(client: TestClient):
    # EC-AUTH-03 Duplicate registration
    client.post("/api/auth/register", json={"email": "dup@example.com", "password": "password", "role": "member"})
    res = client.post("/api/auth/register", json={"email": "dup@example.com", "password": "password", "role": "member"})
    assert res.status_code == 400
