import requests

BASE_URL = "http://localhost:8000/api/v1"

# Register
reg_data = {
    "email": "dashboard_test@scamshield.ai",
    "password": "Password123!",
    "full_name": "Test User"
}
requests.post(f"{BASE_URL}/auth/register", json=reg_data)

# Login
login_data = {
    "username": "dashboard_test@scamshield.ai",
    "password": "Password123!"
}
res = requests.post(f"{BASE_URL}/auth/login", data=login_data)
token = res.json().get("access_token")

if not token:
    print("Login failed:", res.json())
    exit(1)

# Stats
headers = {"Authorization": f"Bearer {token}"}
stats_res = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
print("Status Code:", stats_res.status_code)
print("Response:", stats_res.json())
