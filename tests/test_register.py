import pytest
from utils import ROUTES, generate_unique_email

"""
Tests for the user registration functionality. Validates the registration process
for both owner and clinic accounts, including validation of email uniqueness and
password requirements.
"""

@pytest.mark.anyio
async def test_register_owner_success(client):
    email = generate_unique_email("owner")
    response = await client.post(ROUTES["register_owner"], json={
        "name": "Carlos Herrera",
        "email": email,
        "password": "StrongPass123!",
        "confirmPassword": "StrongPass123!",
        "phone": "573001234567",
        "address": "Calle 123 #45-67"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "token" in data
    assert data["user"]["email"] == email
    assert data["user"]["userType"] == "owner"

@pytest.mark.anyio
async def test_register_owner_duplicate_email(client):
    email = generate_unique_email("owner_dup")

    await client.post(ROUTES["register_owner"], json={
        "name": "Carlos Herrera",
        "email": email,
        "password": "StrongPass123!",
        "confirmPassword": "StrongPass123!",
        "phone": "573001234567",
        "address": "Calle 123 #45-67"
    })

    response = await client.post(ROUTES["register_owner"], json={
        "name": "Carlos Herrera",
        "email": email,
        "password": "StrongPass123!",
        "confirmPassword": "StrongPass123!",
        "phone": "573001234567",
        "address": "Calle 123 #45-67"
    })

    assert response.status_code == 400
    assert "Email already registered." in response.text

@pytest.mark.anyio
async def test_register_owner_password_mismatch(client):
    response = await client.post(ROUTES["register_owner"], json={
        "name": "Carlos Herrera",
        "email": generate_unique_email("owner_mismatch"),
        "password": "StrongPass123!",
        "confirmPassword": "WrongPassword!",
        "phone": "573001234567",
        "address": "Calle 123 #45-67"
    })

    assert response.status_code == 422
    assert "Passwords do not match" in response.text

@pytest.mark.anyio
async def test_register_clinic_success(client):
    email = generate_unique_email("clinic")
    response = await client.post(ROUTES["register_clinic"], json={
        "name": "Clínica Vida",
        "email": email,
        "password": "SecureP@ssword123",
        "confirmPassword": "SecureP@ssword123",
        "phone": "57123456789",
        "address": "Carrera 7 #45-89",
        "locality": "Bosa"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "token" in data
    assert data["user"]["email"] == email
    assert data["user"]["userType"] == "clinic"
    assert data["user"]["locality"] == "Bosa"

@pytest.mark.anyio
async def test_register_clinic_missing_locality(client):
    response = await client.post(ROUTES["register_clinic"], json={
        "name": "Clínica Vida",
        "email": generate_unique_email("clinic_missing"),
        "password": "SecureP@ssword123",
        "confirmPassword": "SecureP@ssword123",
        "phone": "57123456789",
        "address": "Carrera 7 #45-89"
    })

    assert response.status_code == 422
    assert "locality" in str(response.content)

@pytest.mark.anyio
async def test_register_owner_weak_password(client):
    """Test registration with weak passwords"""
    test_cases = [
        ("123", "too short"),
        ("password", "no numbers or special chars"),
        ("12345678", "no letters"),
        ("Password", "no numbers or special chars"),
    ]
    
    for weak_password, description in test_cases:
        response = await client.post(ROUTES["register_owner"], json={
            "name": "Test User",
            "email": generate_unique_email("weak_pass"),
            "password": weak_password,
            "confirmPassword": weak_password,
            "phone": "573001234567",
            "address": "Test Address"
        })
        
        assert response.status_code == 422, f"Should reject weak password: {description}"
        assert "Password must be at least 8 characters" in response.text or "password" in response.text.lower()

@pytest.mark.anyio
async def test_register_invalid_email_formats(client):
    """Test registration with various invalid email formats"""
    invalid_emails = [
        "notanemail",
        "@domain.com",
        "user@",
        "user..double@domain.com",
        "user@domain",
        "user name@domain.com",
    ]
    
    for invalid_email in invalid_emails:
        response = await client.post(ROUTES["register_owner"], json={
            "name": "Test User",
            "email": invalid_email,
            "password": "ValidPass123!",
            "confirmPassword": "ValidPass123!",
            "phone": "573001234567",
            "address": "Test Address"
        })
        
        assert response.status_code == 422
        assert "email" in response.text.lower()

@pytest.mark.anyio
async def test_register_missing_required_fields(client):
    """Test registration with missing required fields"""
    base_data = {
        "name": "Test User",
        "email": generate_unique_email("missing"),
        "password": "ValidPass123!",
        "confirmPassword": "ValidPass123!",
        "phone": "573001234567",
        "address": "Test Address"
    }
    
    required_fields = ["name", "email", "password", "confirmPassword", "phone", "address"]
    
    for field in required_fields:
        data = base_data.copy()
        del data[field]
        
        response = await client.post(ROUTES["register_owner"], json=data)
        assert response.status_code == 422
        assert field in response.text

@pytest.mark.anyio
async def test_register_clinic_invalid_locality(client):
    """Test clinic registration with invalid locality values"""
    invalid_localities = ["", "   ", "NonExistentLocality", "123", None]
    
    for locality in invalid_localities:
        data = {
            "name": "Test Clinic",
            "email": generate_unique_email("invalid_locality"),
            "password": "ValidPass123!",
            "confirmPassword": "ValidPass123!",
            "phone": "573001234567",
            "address": "Test Address"
        }
        
        if locality is not None:
            data["locality"] = locality
            
        response = await client.post(ROUTES["register_clinic"], json=data)
        assert response.status_code == 422