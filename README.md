# Authentication Service Test Suite

This repository contains an automated test suite for testing authentication-related endpoints and functionalities. The suite covers various authentication flows including registration, login, password management, profile operations, and token verification.

## Features

- ✅ User Registration Tests
- ✅ Login/Logout Flow Tests
- ✅ Password Management (Change, Reset, Forgot Password)
- ✅ Profile Management (Get, Update, Delete)
- ✅ Token Verification Tests
- ✅ Multi-step Authentication Tests
- 📊 Automated Test Report Generation

## Prerequisites

- Python 3.x
- pip

## Installation

1. Clone the repository:
```bash
git clone https://github.com/CobrasOrg/auth-service-tests
cd auth-service-tests
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Before running the tests, make sure to set up your environment variables. Create a `.env` file in the root directory with the necessary configuration:

```env
# Add your environment variables here
API_BASE_URL=your_api_base_url
MONGODB_URL=mongo_connection_url
MONGODB_DB_NAME=test_database
```

## Running the Tests

### Run all tests
```bash
pytest
```

### Run specific test modules
```bash
# Run login tests
pytest tests/test_login.py

# Run registration tests
pytest tests/test_register.py
```

## Test Reports

The test suite includes automatic report generation in PDF (custom implementation in `tests/report_generator.py`)

Reports are saved in the `reports/` directory with timestamps for easy tracking.

## Test Structure

```
tests/
├── test_login.py          # Login flow tests
├── test_register.py       # Registration flow tests
├── test_change_password.py # Password change tests
├── test_forgot_password.py # Password recovery tests
├── test_reset_password.py  # Password reset tests
├── test_get_profile.py    # Profile retrieval tests
├── test_update_profile.py # Profile update tests
├── test_delete_account.py # Account deletion tests
├── test_logout.py         # Logout flow tests
├── test_verify_token.py   # Token verification tests
├── test_multi_step.py     # Multi-step authentication tests
├── report_generator.py    # Report generation utilities
└── utils.py              # Common test utilities
```

## Dependencies

- pytest: Testing framework
- httpx: HTTP client for making API requests
- pytest-asyncio: Async support for pytest
- motor: MongoDB async driver
- python-dotenv: Environment variable management
- pymongo: MongoDB driver
- reportlab: PDF report generation
