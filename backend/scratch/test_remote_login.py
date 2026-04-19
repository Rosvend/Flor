import requests

def test_remote_login():
    url = "http://127.0.0.1:8000/api/v1/auth/login"
    payload = {
        "correo_electronico": "admin@flor.com",
        "password": "admin123"
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_remote_login()
