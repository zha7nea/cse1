import pytest
from api import app, db
from api import Customer, CustomerCall

# Define the test client as a fixture
@pytest.fixture(scope='module')
def test_client():
    # Configuring the app for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    # Using the app context to set up the database and test client
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create tables
            yield client  # Provide the test client to tests
            db.session.remove()  # Cleanup after tests
            db.drop_all()  # Drop tables

