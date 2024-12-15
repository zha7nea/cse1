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


# Sample test to check if invalid customer creation returns 400
def test_create_invalid_customer(test_client):
    response = test_client.post('/customers', json={})  # Missing required field
    assert response.status_code == 400  # Expect a 400 error due to missing data

# Test to check if a call can be created for an existing customer
def test_create_call(test_client):
    # Add a customer first
    customer_data = {"customer_Other_Details": "Test customer"}
    response = test_client.post('/customers', json=customer_data)
    customer_id = response.get_json()['customer_ID']

    call_data = {
        "customer_ID": customer_id,
        "call_Date_Time": "2024-12-12 12:00:00",
        "call_Outcome_Code": "Success",
        "call_Status_Code": "Completed"
    }
    response = test_client.post('/customer_calls', json=call_data)
    assert response.status_code == 201  # Check if the call creation returns 201 Created

# Test to check if a specific customer can be retrieved
def test_get_customer_by_id(test_client):
    # Create a customer
    customer_data = {"customer_Other_Details": "Specific Test Customer"}
    create_response = test_client.post('/customers', json=customer_data)
    customer_id = create_response.get_json()['customer_ID']