import pytest
from utils import ROUTES, auth_headers, get_auth_token

"""
Tests for the logout functionality. Verifies successful logout operations,
token revocation, and proper handling of invalid logout attempts.
"""

@pytest.mark.anyio
async def test_logout_success(client):
    token = await get_auth_token(client)

    response = await client.post(
        ROUTES["logout"],
        headers=auth_headers(token)
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Logged out successfully."

@pytest.mark.anyio
async def test_logout_invalid_token(client):
    response = await client.post(
        ROUTES["logout"],
        headers=auth_headers("totally.invalid.token")
    )

    assert response.status_code == 400
    assert "Invalid token or already expired" in response.text

@pytest.mark.anyio
async def test_logout_already_revoked_token(client):
    token = await get_auth_token(client)

    first = await client.post(
        ROUTES["logout"],
        headers=auth_headers(token)
    )
    assert first.status_code == 200
    assert "Logged out successfully." in first.text

    second = await client.post(
        ROUTES["logout"],
        headers=auth_headers(token)
    )
    assert second.status_code == 200
    assert "Logged out successfully." in second.text

@pytest.mark.anyio
async def test_logout_missing_token(client):
    response = await client.post(ROUTES["logout"])

    assert response.status_code == 403
    assert "Not authenticated" in response.text
