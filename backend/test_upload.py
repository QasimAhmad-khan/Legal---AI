import requests

email = "testpdf3@example.com"
r1 = requests.post("http://localhost:8001/api/auth/register", json={"email": email, "password": "password", "role": "admin"})
print("Reg:", r1.status_code, r1.text)

r2 = requests.post("http://localhost:8001/api/auth/login", data={"username": email, "password": "password"})
print("Login:", r2.status_code, r2.text)
token = r2.json().get("access_token")

files = {"file": ("test.pdf", b"%PDF-1.4 mock pdf data", "application/pdf")}
headers = {"Authorization": f"Bearer {token}"}
r3 = requests.post("http://localhost:8001/api/documents", files=files, headers=headers)
print("Upload:", r3.status_code, r3.text)
