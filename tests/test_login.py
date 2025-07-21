import pytest
from utils import ROUTES, generate_unique_email, register_test_user

"""
Tests for the authentication login endpoint. Verifies successful login attempts,
invalid credentials handling, and various error scenarios.
"""

@pytest.mark.anyio
async def test_login_success(client):
    email = generate_unique_email("login")
    password = "SecureLogin123!"

    await register_test_user(
        client,
        email=email,
        password=password,
        name="Lucía Pérez"
    )

    response = await client.post(ROUTES["login"], json={
        "email": email,
        "password": password
    })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "token" in data
    assert data["user"]["email"] == email

@pytest.mark.anyio
async def test_login_unregistered_email(client):
    response = await client.post(ROUTES["login"], json={
        "email": generate_unique_email("no_user"),
        "password": "DoesntMatter123"
    })

    assert response.status_code == 401
    assert "Invalid email or password" in response.text

@pytest.mark.anyio
async def test_login_wrong_password(client):
    email = generate_unique_email("wrongpass")
    correct_password = "CorrectP@ss123"
    wrong_password = "WrongPass456"

    await register_test_user(
        client,
        email=email,
        password=correct_password,
        name="Andrés Díaz",
        phone="573002223344",
        address="Av. Siempre Viva 742"
    )

    response = await client.post(ROUTES["login"], json={
        "email": email,
        "password": wrong_password
    })

    assert response.status_code == 401
    assert "Invalid email or password" in response.text

@pytest.mark.anyio
async def test_login_invalid_email_format(client):
    response = await client.post(ROUTES["login"], json={
        "email": "invalid-email",
        "password": "Password123"
    })

    assert response.status_code == 422
    assert "value is not a valid email address" in response.text

@pytest.mark.anyio
async def test_login_missing_password(client):
    response = await client.post(ROUTES["login"], json={
        "email": "someone@example.com"
    })

    assert response.status_code == 422
    assert "password" in response.text

@pytest.mark.anyio
async def test_login_empty_credentials(client):
    """Test login with empty email/password"""
    test_cases = [
        {"email": "", "password": "ValidPass123!"},
        {"email": "valid@email.com", "password": ""},
        {"email": "", "password": ""},
    ]
    
    for credentials in test_cases:
        response = await client.post(ROUTES["login"], json=credentials)
        assert response.status_code in [401, 422]

@pytest.mark.anyio
async def test_login_case_sensitivity(client):
    """Test if login is case sensitive for email"""
    email = generate_unique_email("case_test").lower()
    password = "CaseSensitive123!"
    
    await register_test_user(client, email=email, password=password, name="Case Test")
    
    response = await client.post(ROUTES["login"], json={
        "email": email.upper(),
        "password": password
    })
    
    assert response.status_code == 200