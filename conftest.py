import os
import pytest
from dotenv import load_dotenv
from datetime import datetime
from httpx import AsyncClient
from pymongo.errors import ServerSelectionTimeoutError
from motor.motor_asyncio import AsyncIOMotorClient
from tests.report_generator import TestReportGenerator


load_dotenv()

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

API_URL = os.getenv("API_URL", "http://localhost:8000")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "petmatchDB_test")

@pytest.fixture(scope="function")
async def client():
    async with AsyncClient(base_url=API_URL) as ac:
        yield ac

@pytest.fixture(scope="function", autouse=True)
async def clean_test_db():
    try:
        client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=2000)
        await client.server_info()
    except ServerSelectionTimeoutError:
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        
    db = client[MONGODB_DB_NAME]
    await db["users"].delete_many({})
    await db["revoked_tokens"].delete_many({})
    
    yield
    
    await db["users"].delete_many({})
    await db["revoked_tokens"].delete_many({})
    client.close()

def pytest_sessionfinish(session, exitstatus):
    test_results = []
    for item in session.items:
        report = item.reportinfo()
        call = item._calling_fixtures if hasattr(item, '_calling_fixtures') else None
        outcome = 'skipped'
        duration = 0

        if hasattr(item, 'rep_call'):
            outcome = 'passed' if item.rep_call.passed else 'failed'
            duration = item.rep_call.duration
        elif hasattr(item, 'rep_setup') and item.rep_setup.skipped:
            outcome = 'skipped'

        test_results.append({
            'name': item.name,
            'outcome': outcome,
            'duration': duration
        })

    os.makedirs("reports", exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"reports/reporte_pruebas_auth_BE_{timestamp}.pdf"

    generator = TestReportGenerator(test_results)
    generator.generate_report(filename)

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == 'call':
        item.rep_call = report
    elif report.when == 'setup':
        item.rep_setup = report