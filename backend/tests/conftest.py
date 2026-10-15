import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.storage import reset


@pytest.fixture(autouse=True)
def clear_store():
    reset()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
