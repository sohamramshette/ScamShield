import requests

BASE_URL = "http://localhost:8000/api/v1"
user_payload = {"email": "test@example.com", "password": "password123"}
auth_token = None

def test_health():
    res = requests.get(f"{BASE_URL}/health")
    print(f"Health: {res.status_code} {res.text}")

def test_register():
    res = requests.post(f"{BASE_URL}/auth/register", json=user_payload)
    print(f"Register: {res.status_code} {res.text}")

def test_login():
    global auth_token
    # Form data for OAuth2PasswordRequestForm
    res = requests.post(f"{BASE_URL}/auth/login", data={"username": user_payload["email"], "password": user_payload["password"]})
    print(f"Login: {res.status_code} {res.text}")
    if res.status_code == 200:
        auth_token = res.json().get("access_token")

def test_website_scanner():
    headers = {"Authorization": f"Bearer {auth_token}"}
    res = requests.post(f"{BASE_URL}/scanners/website", headers=headers, json={"url": "http://suspicious-login-update.com"})
    print(f"Website Scanner: {res.status_code} {res.text}")

def test_qr_scanner():
    headers = {"Authorization": f"Bearer {auth_token}"}
    res = requests.post(f"{BASE_URL}/scanners/qr", headers=headers, json={"qr_content": "http://malicious.com"})
    print(f"QR Scanner: {res.status_code} {res.text}")

def test_upi_scanner():
    headers = {"Authorization": f"Bearer {auth_token}"}
    res = requests.post(f"{BASE_URL}/scanners/upi", headers=headers, json={"upi_id": "scammer@ybl"})
    print(f"UPI Scanner: {res.status_code} {res.text}")

def test_history():
    headers = {"Authorization": f"Bearer {auth_token}"}
    res = requests.get(f"{BASE_URL}/history/recent", headers=headers)
    print(f"History: {res.status_code} {res.text}")

print("--- RUNNING BACKEND AUDIT ---")
test_health()
test_register()
test_login()
if auth_token:
    test_website_scanner()
    test_qr_scanner()
    test_upi_scanner()
    test_history()
