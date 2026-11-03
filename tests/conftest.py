import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from config import Config

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    # Disable SameSite cookie restriction so test client cookies work
    SESSION_COOKIE_SAMESITE = None
    SESSION_COOKIE_SECURE = False

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')

    class _TestConfig(TestConfig):
        DATABASE_PATH = db_path

    application = create_app(_TestConfig)

    yield application

    os.close(db_fd)
    if os.path.exists(db_path):
        try:
            os.unlink(db_path)
        except OSError:
            pass

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """Test client fixture with a pre-registered and logged-in user."""
    # Register
    client.post('/api/auth/register', json={
        'full_name': 'Test User',
        'email': 'authtest@expensemate.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    # Explicitly login to ensure session cookie is set
    client.post('/api/auth/login', json={
        'email': 'authtest@expensemate.com',
        'password': 'password123'
    })
    return client
