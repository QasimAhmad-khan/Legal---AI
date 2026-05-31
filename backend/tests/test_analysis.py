from fastapi.testclient import TestClient

def get_token(client: TestClient):
    client.post("/api/auth/register", json={"email": "analysis@example.com", "password": "password", "role": "admin"})
    res = client.post("/api/auth/login", data={"username": "analysis@example.com", "password": "password"})
    return res.json()["access_token"]

def test_analysis_streaming(client: TestClient):
    token = get_token(client)
    
    # Upload doc
    res = client.post("/api/documents", files={"file": ("test.txt", b"Standard confidentiality clause.", "text/plain")}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    doc_id = res.json()["id"]
    
    # Analyze doc (stream)
    # We test the SSE endpoint
    # Note: doc needs to be "processed" to be analyzed
    # Background task finishes fast, so we expect 200.
    import time
    time.sleep(0.5)  # give it a sec to process
    res = client.post(f"/api/analysis/{doc_id}/analyze", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200

def test_analysis_report(client: TestClient):
    token = get_token(client)
    res = client.post("/api/documents", files={"file": ("test2.txt", b"Another clause.", "text/plain")}, headers={"Authorization": f"Bearer {token}"})
    doc_id = res.json()["id"]
    
    res = client.get(f"/api/analysis/{doc_id}/report", headers={"Authorization": f"Bearer {token}"})
    # Might be 404 or empty if analysis not run yet, or 200 if it works.
    # In our implementation, we'll check it doesn't crash 500
    assert res.status_code in [200, 404]
