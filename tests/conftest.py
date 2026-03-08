import pytest
from src import create_app, db
from src.models import User, Voter
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False

@pytest.fixture(scope='module')
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def admin_user(app):
    with app.app_context():
        voter = Voter(cedula="admin")
        db.session.add(voter)
        db.session.commit()

        user = User(username="admin", voter_id=voter.id, is_admin=True)
        user.set_password("admin")
        db.session.add(user)
        db.session.commit()
        
        yield user
        
        db.session.delete(user)
        db.session.delete(voter)
        db.session.commit()

@pytest.fixture(scope='function')
def regular_user(app):
    with app.app_context():
        voter = Voter(cedula="user")
        db.session.add(voter)
        db.session.commit()

        user = User(username="user", voter_id=voter.id, is_admin=False)
        user.set_password("user")
        db.session.add(user)
        db.session.commit()

        yield user
        
        db.session.delete(user)
        db.session.delete(voter)
        db.session.commit()
