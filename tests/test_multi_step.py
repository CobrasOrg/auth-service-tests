import pytest
from utils import ROUTES, auth_headers, generate_unique_email, get_auth_token, register_test_user

"""
Tests for complete user lifecycle scenarios. Verifies end-to-end flows combining
multiple operations like registration, login, profile updates, and account
management for both owner and clinic users.
"""

@pytest.mark.anyio
async def test_complete_user_lifecycle_owner(client):
    """Test complete user lifecycle for owner: register -> login -> update -> change password -> delete"""
    email = generate_unique_email("lifecycle_owner")
    initial_password = "InitialPass123!"
    
    register_response = await client.post(ROUTES["register_owner"], json={
        "name": "Lifecycle Test Owner",
        "email": email,
        "password": initial_password,
        "confirmPassword": initial_password,
        "phone": "573001234567",
        "address": "Initial Address"
    })
    assert register_response.status_code == 201
    token = register_response.json()["token"]
    
    verify_response = await client.post(ROUTES["verify_token"], headers=auth_headers(token))
    assert verify_response.status_code == 200

    login_response = await client.post(ROUTES["login"], json={
        "email": email,
        "password": initial_password
    })
    assert verify_response.status_code == 200
    
    profile_response = await client.get(ROUTES["profile"], headers=auth_headers(token))
    assert profile_response.status_code == 200
    assert profile_response.json()["userType"] == "owner"
    
    update_response = await client.patch(ROUTES["update_profile"], headers=auth_headers(token), json={
        "name": "Updated Owner Name",
        "phone": "573009876543"
    })
    assert update_response.status_code == 200
    
    new_password = "NewPassword123!"
    change_pass_response = await client.put(ROUTES["change_password"], json={
        "currentPassword": initial_password,
        "newPassword": new_password,
        "confirmPassword": new_password
    }, headers=auth_headers(token))
    assert change_pass_response.status_code == 200
    
    login_response = await client.post(ROUTES["login"], json={
        "email": email,
        "password": new_password
    })
    assert login_response.status_code == 200
    new_token = login_response.json()["token"]
    
    delete_response = await client.delete(ROUTES["delete_account"], headers=auth_headers(new_token))
    assert delete_response.status_code == 200
    
    profile_after_delete = await client.get(ROUTES["profile"], headers=auth_headers(new_token))
    assert profile_after_delete.status_code == 401

@pytest.mark.anyio
async def test_complete_user_lifecycle_clinic(client):
    """Test complete user lifecycle for clinic with locality-specific operations"""
    email = generate_unique_email("lifecycle_clinic")
    password = "ClinicPass123!"
    
    register_response = await client.post(ROUTES["register_clinic"], json={
        "name": "Lifecycle Test Clinic",
        "email": email,
        "password": password,
        "confirmPassword": password,
        "phone": "571234567890",
        "address": "Clinic Address",
        "locality": "Chapinero"
    })
    assert register_response.status_code == 201
    token = register_response.json()["token"]
    
    profile_response = await client.get(ROUTES["profile"], headers=auth_headers(token))
    assert profile_response.status_code == 200
    profile_data = profile_response.json()
    assert profile_data["userType"] == "clinic"
    assert profile_data["locality"] == "Chapinero"
    
    update_response = await client.patch(ROUTES["update_profile"], headers=auth_headers(token), json={
        "name": "Updated Clinic Name",
        "locality": "Usaquén"
    })
    assert update_response.status_code == 200
    assert update_response.json()["locality"] == "Usaquén"
    
    updated_profile = await client.get(ROUTES["profile"], headers=auth_headers(token))
    assert updated_profile.json()["locality"] == "Usaquén"

@pytest.mark.anyio
async def test_password_reset_flow_complete(client):
    """Test complete password reset flow"""
    email = generate_unique_email("reset_flow")
    old_password = "OldFlowPass123!"
    new_password = "NewFlowPass456!"
    
    await register_test_user(client, email=email, password=old_password, name="Reset Flow Test")
    
    login_response = await client.post(ROUTES["login"], json={
        "email": email,
        "password": old_password
    })
    assert login_response.status_code == 200
    
    forgot_response = await client.post(ROUTES["forgot_password"], json={"email": email})
    assert forgot_response.status_code == 200
    
    token_response = await client.post(ROUTES["debug_reset_token"], json={"email": email})
    reset_token = token_response.json()["token"]
    
    reset_response = await client.post(ROUTES["reset_password"], json={
        "token": reset_token,
        "newPassword": new_password,
        "confirmPassword": new_password
    })
    assert reset_response.status_code == 200

    old_login_response = await client.post(ROUTES["login"], json={
        "email": email,
        "password": old_password
    })
    assert old_login_response.status_code == 401

    new_login_response = await client.post(ROUTES["login"], json={
        "email": email,
        "password": new_password
    })
    assert new_login_response.status_code == 200

@pytest.mark.anyio
async def test_concurrent_login_logout_flow(client):
    """Test multiple login sessions and logout behavior"""
    email = generate_unique_email("concurrent")
    password = "ConcurrentPass123!"

    initial_token = await get_auth_token(client, email=email, password=password)
    assert initial_token

    login_sessions = [initial_token]

    for _ in range(3):
        login_response = await client.post(ROUTES["login"], json={
            "email": email,
            "password": password
        })
        assert login_response.status_code == 200
        token = login_response.json().get("token")
        assert token, "Token missing in login response"
        login_sessions.append(token)

    for token in login_sessions:
        verify_response = await client.post(ROUTES["verify_token"], headers=auth_headers(token))
        assert verify_response.status_code == 200, f"Token {token} should be valid"

    logout_response = await client.post(ROUTES["logout"], headers=auth_headers(login_sessions[0]))
    assert logout_response.status_code == 200

    invalid_verify = await client.post(ROUTES["verify_token"], headers=auth_headers(login_sessions[0]))
    assert invalid_verify.status_code == 401

    for remaining_token in login_sessions[1:]:
        verify_response = await client.post(ROUTES["verify_token"], headers=auth_headers(remaining_token))
        assert verify_response.status_code == 200, f"Token {remaining_token} should still be valid"


@pytest.mark.anyio
async def test_cross_user_type_operations(client):
    """Test that owner operations don't work with clinic tokens and vice versa"""
    owner_token = await get_auth_token(client, user_type="owner")
    clinic_token = await get_auth_token(client, user_type="clinic")
    
    owner_locality_update = await client.patch(
        ROUTES["update_profile"],
        headers=auth_headers(owner_token),
        json={"locality": "Chapinero"}
    )
    assert owner_locality_update.status_code == 400
    assert "Only clinics can update 'locality'" in owner_locality_update.text
    
    clinic_locality_update = await client.patch(
        ROUTES["update_profile"],
        headers=auth_headers(clinic_token),
        json={"locality": "Usaquén"}
    )
    assert clinic_locality_update.status_code == 200