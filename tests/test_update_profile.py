import pytest
from utils import ROUTES, auth_headers, get_auth_token

"""
Tests for profile update functionality. Verifies the ability to update user profiles
for both owners and clinics, including validation of input data and proper
authentication checks.
"""

@pytest.mark.anyio
async def test_update_profile_owner_success(client):
    token = await get_auth_token(client, user_type="owner")
    payload = {
        "name": "Carlos Pérez",
        "phone": "573009998877",
        "address": "Calle Nueva 123"
    }

    response = await client.patch(ROUTES["update_profile"], headers=auth_headers(token), json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["name"] == payload["name"]
    assert data["phone"] == payload["phone"]
    assert data["address"] == payload["address"]
    assert data["userType"] == "owner"


@pytest.mark.anyio
async def test_update_profile_owner_invalid_locality(client):
    token = await get_auth_token(client, user_type="owner")

    response = await client.patch(ROUTES["update_profile"], headers=auth_headers(token), json={"locality": "Chapinero"})
    assert response.status_code == 400
    assert "Only clinics can update 'locality'." in response.text

@pytest.mark.anyio
async def test_update_profile_clinic_success(client):
    token = await get_auth_token(client, user_type="clinic")
    payload = {
        "name": "Clínica Nueva",
        "phone": "5712340099",
        "locality": "Usaquén"
    }

    response = await client.patch(ROUTES["update_profile"], headers=auth_headers(token), json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["name"] == payload["name"]
    assert data["phone"] == payload["phone"]
    assert data["locality"] == payload["locality"]
    assert data["userType"] == "clinic"

@pytest.mark.anyio
async def test_update_profile_invalid_email_format(client):
    token = await get_auth_token(client)

    response = await client.patch(ROUTES["update_profile"], headers=auth_headers(token), json={"email": "not-an-email"})
    assert response.status_code == 422

@pytest.mark.anyio
async def test_update_profile_revoked_token(client):
    token = await get_auth_token(client)
    await client.post(ROUTES["logout"], headers=auth_headers(token))

    response = await client.patch(ROUTES["update_profile"], headers=auth_headers(token), json={"name": "Nuevo Nombre"})
    assert response.status_code == 401
    assert "Token has been revoked" in response.text

@pytest.mark.anyio
async def test_update_profile_no_auth(client):
    response = await client.patch(ROUTES["update_profile"], json={"name": "Anon"})
    assert response.status_code == 403
    assert "Not authenticated" in response.text
