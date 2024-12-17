import pytest
from flask import jsonify
from api import create_app, db, Customer, CustomerCall

@pytest.fixture
def app():
    app = create_app({
        'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://root:root@localhost/callcenter',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })

    with app.app_context():
        db.create_all()
        db.session.begin()

    yield app 

    with app.app_context():
        db.session.rollback()
        db.session.remove() 

@pytest.fixture
def client(app):
    return app.test_client()

def test_home(client):
    response = client.get('/')
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data['message'] == 'Call Center Management System'

def test_get_customers(client):
    login_response = client.post('/login', json={'username': 'admin', 'password': 'admin'})
    
    # Ensure login was successful
    assert login_response.status_code == 200
    
    # Get the token from the response
    token = login_response.get_json()['access_token']  # Access the correct key for the token
    
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/customers', headers=headers)
    
    # Ensure the response is successful
    assert response.status_code == 200

def test_get_customer(client):
    # Obtain a valid token by logging in
    login_response = client.post('/login', json={'username': 'admin', 'password': 'admin'})
    assert login_response.status_code == 200
    token = login_response.get_json()['access_token']  # Access the correct key for the token
    
    # Make authenticated request to retrieve a specific customer
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/customers/2', headers=headers)  # Replace with a specific customer ID

    # Ensure the response is successful
    assert response.status_code == 200
    
    # Get the response JSON data
    json_data = response.get_json()
    
    # Ensure that the customer ID matches
    assert json_data['customer_id'] == 2
    
    # Ensure that the returned customer data includes the expected fields
    assert 'customer_other_details' in json_data  # Make sure other details are included
    assert isinstance(json_data['customer_other_details'], str) or json_data['customer_other_details'] is None  # Validate the type of 'customer_Other_Details'

# Test for creating an account
def test_create_account(client):
    account_data = {     
        "customer_other_details": "New customer with VIP status"
    }
    response = client.post('/customers', json=account_data)
    json_data = response.get_json()
    assert response.status_code == 201
    assert json_data['message'] == 'Account created successfully'