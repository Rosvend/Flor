import requests

def test_me():
    # Login first to get token
    login_url = "http://127.0.0.1:8001/api/v1/auth/login"
    login_payload = {
        "correo_electronico": "admin@flor.com",
        "password": "admin123"
    }
    login_resp = requests.post(login_url, json=login_payload)
    token = login_resp.json()["access_token"]
    
    # Test /me
    me_url = "http://127.0.0.1:8001/api/v1/auth/me"
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = requests.get(me_url, headers=headers)
    
    print(f"Me Status Code: {me_resp.status_code}")
    print(f"Me Response: {me_resp.text}")

if __name__ == "__main__":
    test_me()
