import pytest
from utils import ROUTES, generate_unique_email, register_test_user

"""
Tests for the forgot password functionality. Validates the password recovery
request process, including handling of existing and non-existing email addresses
and rate limiting.
"""

@pytest.mark.anyio
async def test_forgot_password_with_existing_email(client):
    email = generate_unique_email()
    password = "Secure123!"
    
    await register_test_user(
        client,
        email=email,
        password=password,
        name="Luisa Márquez",
        phone="573000112233",
        address="Carrera 7 #45-23"
    )

    response = await client.post(ROUTES["forgot_password"], json={"email": email})

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Password reset email sent."

@pytest.mark.anyio
async def test_forgot_password_with_nonexistent_email(client):
    fake_email = generate_unique_email("nonexistent")

    response = await client.post(ROUTES["forgot_password"], json={"email": fake_email})

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Password reset email sent."

@pytest.mark.anyio
async def test_forgot_password_with_invalid_email_format(client):
    response = await client.post(ROUTES["forgot_password"], json={"email": "not-an-email"})

    assert response.status_code == 422
    assert "value is not a valid email address" in response.text

@pytest.mark.anyio
async def test_forgot_password_with_missing_email(client):
    response = await client.post(ROUTES["forgot_password"], json={})

    assert response.status_code == 422
    assert "email" in response.text

@pytest.mark.anyio
async def test_forgot_password_multiple_requests(client):
    """Test multiple forgot password requests for same email"""
    email = generate_unique_email("multiple_forgot")
    await register_test_user(client, email=email, password="Test123!", name="Multi Test")
    
    for i in range(3):
        response = await client.post(ROUTES["forgot_password"], json={"email": email})
        assert response.status_code == 200