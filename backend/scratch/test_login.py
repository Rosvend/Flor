import sys
from pathlib import Path

# Add backend to sys.path
backend_path = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_path))

from src.infrastructure import container
from src.application.use_cases.login_user import LoginUser, LoginInput

def test_login():
    print(f"Testing login with {container.user_repository.__class__.__name__}")
    
    use_case = LoginUser(
        container.user_repository,
        container.password_hasher,
        container.token_generator
    )
    
    try:
        result = use_case.execute(LoginInput(
            correo_electronico="admin@flor.com",
            password="admin123"
        ))
        print("Login SUCCESS!")
        print(f"Token: {result.access_token[:20]}...")
    except Exception as e:
        print(f"Login FAILED: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_login()
