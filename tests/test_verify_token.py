import pytest
from utils import ROUTES, auth_headers, generate_unique_email, get_auth_token

"""
Tests for token verification functionality. Validates the behavior of the token
verification endpoint with valid, invalid, and revoked tokens, as well as
various malformed token scenarios.
"""

@pytest.mark.anyio
async def test_verify_valid_token(client):
    email = generate_unique_email("verify")
    password = "ValidToken123!"

    token = await get_auth_token(client, email=email, password=password)
    
    response = await client.post(ROUTES["verify_token"], headers=auth_headers(token))

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["email"] == email
    assert body["user_type"] == "owner"
    assert "user_id" in body

@pytest.mark.anyio
async def test_verify_invalid_token(client):
    invalid_token = "this.is.not.a.valid.token"

    response = await client.post(ROUTES["verify_token"], headers=auth_headers(invalid_token))

    assert response.status_code == 401
    assert "Invalid Access token." in response.text

@pytest.mark.anyio
async def test_verify_revoked_token(client):
    email = generate_unique_email("verify")
    password = "RevokedToken123!"

    token = await get_auth_token(client, email=email, password=password)
    await client.post(ROUTES["logout"], headers=auth_headers(token))

    response = await client.post(ROUTES["verify_token"], headers=auth_headers(token))
    assert response.status_code == 401
    assert "Token has been revoked" in response.text

@pytest.mark.anyio
async def test_verify_token_no_auth_header(client):
    response = await client.post(ROUTES["verify_token"])

    assert response.status_code == 403
    assert "Not authenticated" in response.text

@pytest.mark.anyio
async def test_verify_malformed_tokens(client):
    """Test token verification with malformed tokens"""
    malformed_tokens = [
        "not.a.token",
        "header.payload",
        "too.many.parts.here.extra",
        "bearer token",
    ]
    
    for token in malformed_tokens:
        response = await client.post(ROUTES["verify_token"], headers=auth_headers(token))
        assert response.status_code == 401