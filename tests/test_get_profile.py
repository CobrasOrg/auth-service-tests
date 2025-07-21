import pytest
from utils import ROUTES, auth_headers, get_auth_token

"""
Tests for profile retrieval functionality. Validates the ability to fetch user
profiles for both owners and clinics, including authentication and authorization
checks.
"""

@pytest.mark.anyio
async def test_get_profile_owner(client):
    token = await get_auth_token(client, user_type="owner")
    
    response = await client.get(ROUTES["profile"], headers=auth_headers(token))
    assert response.status_code == 200

    body = response.json()
    assert body["userType"] == "owner"
    assert "name" in body
    assert "email" in body
    assert "createdAt" in body
    assert "updatedAt" in body
    assert "password" not in body

@pytest.mark.anyio
async def test_get_profile_clinic(client):
    token = await get_auth_token(
        client, 
        user_type="clinic", 
        name="Clínica Esperanza",
        locality="Chapinero"
    )

    response = await client.get(ROUTES["profile"], headers=auth_headers(token))
    assert response.status_code == 200

    body = response.json()
    assert body["userType"] == "clinic"
    assert body["locality"] == "Chapinero"
    assert "name" in body
    assert "email" in body
    assert "createdAt" in body
    assert "updatedAt" in body
    assert "password" not in body

@pytest.mark.anyio
async def test_get_profile_invalid_token(client):
    fake_token = "this.is.invalid"

    response = await client.get(ROUTES["profile"], headers=auth_headers(fake_token))
    assert response.status_code == 401
    assert "Invalid Access token." in response.text

@pytest.mark.anyio
async def test_get_profile_revoked_token(client):
    token = await get_auth_token(client)

    await client.post(ROUTES["logout"], headers=auth_headers(token))

    response = await client.get(ROUTES["profile"], headers=auth_headers(token))
    assert response.status_code == 401
    assert "Token has been revoked" in response.text

@pytest.mark.anyio
async def test_get_profile_no_auth(client):
    response = await client.get(ROUTES["profile"])
    assert response.status_code == 403
    assert "Not authenticated" in response.text
