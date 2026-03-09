import pytest
from src import create_app, db
from src.models import User
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED = False

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test session."""
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def admin_user(app):
    """Create an admin user for testing."""
    with app.app_context():
        user = User(username='admin', is_admin=True)
        user.set_password('admin_password')
        db.session.add(user)
        db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()

@pytest.fixture(scope='function')
def regular_user(app):
    """Create a regular user for testing."""
    with app.app_context():
        user = User(username='user', is_admin=False)
        user.set_password('user_password')
        db.session.add(user)
        db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()
