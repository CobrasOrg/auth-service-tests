import pytest
from utils import ROUTES, auth_headers, generate_unique_email, get_auth_token

"""
Tests for password change functionality. Validates the process of changing user
passwords, including verification of current password, password strength
requirements, and proper error handling.
"""

@pytest.mark.anyio
async def test_successful_password_change(client):
    email = generate_unique_email("change")
    old_password = "OldPass123!"
    new_password = "NewPass456!"

    token = await get_auth_token(client, email=email, password=old_password)

    response = await client.put(ROUTES["change_password"],
        json={
            "currentPassword": old_password,
            "newPassword": new_password,
            "confirmPassword": new_password
        },
        headers=auth_headers(token)
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "Password changed" in response.json()["message"]

    login_response_new = await client.post(ROUTES["login"], json={
        "email": email,
        "password": new_password
    })

    assert login_response_new.status_code == 200
    assert "token" in login_response_new.json()

@pytest.mark.anyio
async def test_change_password_with_wrong_current_password(client):
    email = generate_unique_email("change")
    correct_password = "RightPass123!"
    wrong_password = "WrongPass123!"
    new_password = "NewValidPass456!"

    token = await get_auth_token(client, email=email, password=correct_password)

    response = await client.put(ROUTES["change_password"],
        json={
            "currentPassword": wrong_password,
            "newPassword": new_password,
            "confirmPassword": new_password
        },
        headers=auth_headers(token)
    )

    assert response.status_code == 401
    assert "Current password is incorrect" in response.text

@pytest.mark.anyio
async def test_change_password_mismatch_confirmation(client):
    email = generate_unique_email("change")
    password = "SomePassword123!"

    token = await get_auth_token(client, email=email, password=password)

    response = await client.put(ROUTES["change_password"],
        json={
            "currentPassword": password,
            "newPassword": "NewPassword123!",
            "confirmPassword": "WrongConfirm123!"
        },
        headers=auth_headers(token)
    )

    assert response.status_code == 422
    assert "Passwords do not match." in response.text

@pytest.mark.anyio
async def test_change_password_weak_new_password(client):
    email = generate_unique_email("change")
    password = "StrongPass123!"

    token = await get_auth_token(client, email=email, password=password)

    response = await client.put(ROUTES["change_password"],
        json={
            "currentPassword": password,
            "newPassword": "123",
            "confirmPassword": "123"
        },
        headers=auth_headers(token)
    )

    assert response.status_code == 422
    assert "Password must be at least 8 characters long" in response.text

@pytest.mark.anyio
async def test_change_password_same_as_current(client):
    """Test changing password to the same password"""
    email = generate_unique_email("same_pass")
    password = "SamePassword123!"
    
    token = await get_auth_token(client, email=email, password=password)
    
    response = await client.put(ROUTES["change_password"], json={
        "currentPassword": password,
        "newPassword": password,
        "confirmPassword": password
    }, headers=auth_headers(token))
    
    assert response.status_code == 200

@pytest.mark.anyio
async def test_change_password_empty_fields(client):
    """Test password change with empty fields"""
    token = await get_auth_token(client)
    
    test_cases = [
        {"currentPassword": "", "newPassword": "New123!", "confirmPassword": "New123!"},
        {"currentPassword": "Current123!", "newPassword": "", "confirmPassword": ""},
        {"currentPassword": "Current123!", "newPassword": "New123!", "confirmPassword": ""},
    ]
    
    for case in test_cases:
        response = await client.put(
            ROUTES["change_password"],
            json=case,
            headers=auth_headers(token)
        )
        assert response.status_code == 422