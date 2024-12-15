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

# Sample test to check if customers can be retrieved
def test_get_customers(test_client):
    response = test_client.get('/customers')
    assert response.status_code == 200  # Check if the response is 200 OK

# Sample test to check if a customer can be created
def test_create_customer(test_client):
    customer_data = {"customer_Other_Details": "Test customer"}
    response = test_client.post('/customers', json=customer_data)
    assert response.status_code == 201  # Check if the response is 201 Created