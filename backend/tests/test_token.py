import requests
import json

# Login
login_response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"email": "test@example.com", "password": "password123"}
)

print("Login response:", login_response.status_code)
login_data = login_response.json()
print("Token:", login_data.get("access_token"))
print("User:", login_data.get("user"))

# Test protected endpoint
token = login_data.get("access_token")
headers = {"Authorization": f"Bearer {token}"}

progress_response = requests.get(
    "http://localhost:8000/api/student/progress?period=week",
    headers=headers
)

print("\nProgress endpoint response:", progress_response.status_code)
print("Response:", progress_response.text)
