import pytest
from db_app import create_app, db

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app('config.TestConfig')

    testing_client = flask_app.test_client()

    ctx = flask_app.app_context()
    ctx.push()

    db.create_all()

    yield testing_client

    db.drop_all()
    ctx.pop()

@pytest.fixture(scope='function')
def init_database():
    db.create_all()

    yield db

    db.session.remove()
    db.drop_all()