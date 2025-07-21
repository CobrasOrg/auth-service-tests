import uuid
from typing import Optional

API_PREFIX = "/api/v1"
ROUTES = {
    "register_owner": f"{API_PREFIX}/auth/register/owner",
    "register_clinic": f"{API_PREFIX}/auth/register/clinic",
    "login": f"{API_PREFIX}/auth/login",
    "logout": f"{API_PREFIX}/auth/logout",
    "forgot_password": f"{API_PREFIX}/auth/forgot-password",
    "reset_password": f"{API_PREFIX}/auth/reset-password",
    "change_password": f"{API_PREFIX}/auth/change-password",
    "verify_token": f"{API_PREFIX}/auth/verify-token",
    "debug_reset_token": f"{API_PREFIX}/debug/reset-token",
    "profile": f"{API_PREFIX}/user/profile",
    "update_profile": f"{API_PREFIX}/user/profile",
    "delete_account": f"{API_PREFIX}/user/account",

}

def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}

def generate_unique_email(prefix: str = "test") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:6]}@example.com"

DEFAULT_PASSWORD = "SecurePass123!"
DEFAULT_USER_DATA = {
    "name": "Test User",
    "phone": "573001234567",
    "address": "Test Address 123"
}

async def register_test_user(client, email: Optional[str] = None, password: str = DEFAULT_PASSWORD, user_type: str = "owner", **kwargs):
    if not email:
        email = generate_unique_email()
    
    user_data = {
        **DEFAULT_USER_DATA,
        "email": email,
        "password": password,
        "confirmPassword": password,
        **kwargs
    }

    if user_type == "clinic":
        user_data["locality"] = kwargs.get("locality", "Suba")
    
    route = ROUTES["register_clinic"] if user_type == "clinic" else ROUTES["register_owner"]
    return await client.post(route, json=user_data)

async def get_auth_token(client, email: Optional[str] = None, password: str = DEFAULT_PASSWORD, **kwargs) -> str:
    if not email:
        email = generate_unique_email()
    
    register_response = await register_test_user(client, email=email, password=password, **kwargs)
    assert register_response.status_code in [200, 201], "User registration failed"
    
    login_response = await client.post(ROUTES["login"], json={
        "email": email,
        "password": password
    })
    assert login_response.status_code == 200, "Login failed"
    
    return login_response.json()["token"]
