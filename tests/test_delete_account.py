import pytest
from utils import ROUTES, auth_headers, get_auth_token

"""
Tests for account deletion functionality. Validates the account deletion process,
including proper authentication verification and handling of post-deletion
access attempts.
"""

@pytest.mark.anyio
async def test_delete_account_success(client):
    token = await get_auth_token(client)

    response = await client.delete(ROUTES["delete_account"], headers=auth_headers(token))
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "Account deleted successfully."

    after_response = await client.get(ROUTES["profile"], headers=auth_headers(token))
    assert after_response.status_code == 401

@pytest.mark.anyio
async def test_delete_account_twice(client):
    token = await get_auth_token(client)

    response = await client.delete(ROUTES["delete_account"], headers=auth_headers(token))
    assert response.status_code == 200

    after_response = await client.delete(ROUTES["delete_account"], headers=auth_headers(token))
    assert after_response.status_code == 401
    assert "Invalid or expired token" in after_response.text

@pytest.mark.anyio
async def test_delete_account_revoked_token(client):
    token = await get_auth_token(client)

    await client.post(ROUTES["logout"], headers=auth_headers(token))

    response = await client.delete(ROUTES["delete_account"], headers=auth_headers(token))
    assert response.status_code == 401
    assert "Token has been revoked" in response.text

@pytest.mark.anyio
async def test_delete_account_no_auth(client):
    response = await client.delete(ROUTES["delete_account"])
    assert response.status_code == 403
    assert "Not authenticated" in response.text
