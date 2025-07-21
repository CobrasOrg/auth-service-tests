import pytest
from utils import ROUTES, generate_unique_email, register_test_user

"""
Tests for password reset functionality. Validates the complete password reset flow,
including token validation, password strength requirements, and error handling
for invalid or expired tokens.
"""

@pytest.mark.anyio
async def test_successful_password_reset(client):
    email = generate_unique_email("reset")
    old_password = "OldPass123!"
    new_password = "NewPass456!"

    await register_test_user(
        client,
        email=email,
        password=old_password,
        name="Lucía Pérez"
    )

    token_response = await client.post(ROUTES["debug_reset_token"], json={"email": email})
    assert token_response.status_code == 200
    token = token_response.json()["token"]

    response = await client.post(ROUTES["reset_password"], json={
        "token": token,
        "newPassword": new_password,
        "confirmPassword": new_password
    })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Password updated successfully" in data["message"]

@pytest.mark.anyio
async def test_password_reset_with_invalid_token(client):
    response = await client.post(ROUTES["reset_password"], json={
        "token": "invalid.token.value",
        "newPassword": "NewPass456!",
        "confirmPassword": "NewPass456!"
    })

    assert response.status_code == 401
    assert "Invalid Reset token." in response.text

@pytest.mark.anyio
async def test_password_reset_with_expired_or_fake_token(client):
    expired_token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjZjdiNzUzZC02NzdlLTQxNzEtYjc5Mi0zYzYwOWQzYTc3MjYiLCJleHAiOjE3NTIzOTE0MTMsInR5cGUiOiJyZXNldCJ9.646_lKdPzF2S3nSEX0yPR1AvF_JhMlCXwMyuoG4TIz0"
    )

    response = await client.post(ROUTES["reset_password"], json={
        "token": expired_token,
        "newPassword": "NewPass456!",
        "confirmPassword": "NewPass456!"
    })

    assert response.status_code == 401
    assert "Reset token has expired." in response.text

@pytest.mark.anyio
async def test_password_reset_with_non_matching_passwords(client):
    email = generate_unique_email("reset")
    old_password = "OldPassword123!"
    
    await register_test_user(
        client,
        email=email,
        password=old_password,
        name="Lucía Pérez"
    )

    token_response = await client.post(ROUTES["debug_reset_token"], json={"email": email})
    token = token_response.json()["token"]

    response = await client.post(ROUTES["reset_password"], json={
        "token": token,
        "newPassword": "NewPassword123!",
        "confirmPassword": "MismatchPassword123!"
    })

    assert response.status_code == 422
    assert "Passwords do not match." in response.text

@pytest.mark.anyio
async def test_password_reset_with_weak_password(client):
    email = generate_unique_email("reset")
    password = "StrongOld123!"
    
    await register_test_user(
        client,
        email=email,
        password=password,
        name="Lucía Pérez"
    )

    token_response = await client.post(ROUTES["debug_reset_token"], json={"email": email})
    token = token_response.json()["token"]

    response = await client.post(ROUTES["reset_password"], json={
        "token": token,
        "newPassword": "123",
        "confirmPassword": "123"
    })

    assert response.status_code == 422
    assert "Password must be at least 8 characters long" in response.text

@pytest.mark.anyio
async def test_reset_token_revocation(client):
    email = generate_unique_email("reset")
    old_password = "OldPass123!"
    new_password = "NewPass456!"

    await register_test_user(
        client,
        email=email,
        password=old_password,
        name="Lucía Pérez"
    )

    token_response = await client.post(ROUTES["debug_reset_token"], json={"email": email})
    token = token_response.json()["token"]

    first_response = await client.post(ROUTES["reset_password"], json={
        "token": token,
        "newPassword": new_password,
        "confirmPassword": new_password
    })

    assert first_response.status_code == 200
    assert first_response.json()["success"] is True

    second_response = await client.post(ROUTES["reset_password"], json={
        "token": token,
        "newPassword": "AnotherPass123!",
        "confirmPassword": "AnotherPass123!"
    })

    assert second_response.status_code == 401
    assert "Token has been revoked" in second_response.text