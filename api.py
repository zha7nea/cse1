from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from security import token_required, role_required, hash_password, login_user
from faker import Faker  # Added for Faker functionality
import random  # For generating random values (like codes)

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "callcenter_backup.sql"

# Initialize the database
db = SQLAlchemy(app)

# Initialize Faker
fake = Faker()

# --- User Model --- 
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # e.g., 'admin' or 'user'

# --- Models --- 
class Customer(db.Model):
    __tablename__ = 'customers'
    customer_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_Other_Details = db.Column(db.String(255), nullable=True)

class CustomerCall(db.Model):
    __tablename__ = 'customer_calls'
    call_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_ID = db.Column(db.Integer, db.ForeignKey('customers.customer_ID'), nullable=False)
    call_Date_Time = db.Column(db.DateTime, nullable=False)
    call_Outcome_Code = db.Column(db.String(10), nullable=False)
    call_Status_Code = db.Column(db.String(10), nullable=False)

    # Relationships
    customer = db.relationship('Customer', backref='calls')

# Create all tables in the database
with app.app_context():
    db.create_all()

# --- Register Route --- 
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username and password are required"}), 400

    # Check if username already exists
    existing_user = User.query.filter_by(username=data["username"]).first()
    if existing_user:
        return jsonify({"error": "Username already taken"}), 400

    # Hash the password before saving it
    hashed_password = hash_password(data["password"])

    # Create a new user
    new_user = User(username=data["username"], password=hashed_password, role="user")  # Default role can be 'user'
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 200

# --- Login Route --- 
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    response, status_code = login_user(data, User)
    return jsonify(response), status_code

# --- Faker Data Generation Route --- 
@app.route('/generate_fake_customers', methods=['POST'])
@token_required
@role_required("admin")
def generate_fake_customers():
    """
    Generate and insert fake customer data into the database.
    """
    try:
        num_records = request.json.get('num_records', 10)  # Default: 10 records
        fake_customers = []

        for _ in range(num_records):
            fake_customer = Customer(
                customer_Other_Details=fake.sentence(nb_words=6)  # Generate fake customer details
            )
            db.session.add(fake_customer)
            fake_customers.append({'customer_Other_Details': fake_customer.customer_Other_Details})

        db.session.commit()
        return jsonify({
            'message': f'{num_records} fake customers generated successfully!',
            'customers': fake_customers
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_fake_calls', methods=['POST'])
@token_required
@role_required("admin")
def generate_fake_calls():
    """
    Generate and insert fake call data into the database.
    """
    try:
        num_records = request.json.get('num_records', 10)  # Default: 10 records
        customers = Customer.query.all()  # Retrieve all customers
        if not customers:
            return jsonify({'error': 'No customers found. Add customers before generating calls.'}), 400

        fake_calls = []

        for _ in range(num_records):
            random_customer = random.choice(customers)
            fake_call = CustomerCall(
                customer_ID=random_customer.customer_ID,
                call_Date_Time=fake.date_time_this_year(),
                call_Outcome_Code=f'OC{random.randint(1, 5)}',  # Random outcome code
                call_Status_Code=f'SC{random.randint(1, 3)}'   # Random status code
            )
            db.session.add(fake_call)
            fake_calls.append({
                'customer_ID': fake_call.customer_ID,
                'call_Date_Time': str(fake_call.call_Date_Time),
                'call_Outcome_Code': fake_call.call_Outcome_Code,
                'call_Status_Code': fake_call.call_Status_Code
            })

        db.session.commit()
        return jsonify({
            'message': f'{num_records} fake customer calls generated successfully!',
            'calls': fake_calls
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- API Endpoints --- 

@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return jsonify([{'customer_ID': c.customer_ID, 'customer_Other_Details': c.customer_Other_Details} for c in customers]), 200

@app.route('/customers', methods=['POST'])
def create_customer():
    data = request.get_json()
    if 'customer_Other_Details' not in data:
        return jsonify({'error': 'Missing customer_Other_Details'}), 400

    new_customer = Customer(customer_Other_Details=data['customer_Other_Details'])
    db.session.add(new_customer)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify({'error': 'Database integrity error'}), 500

    return jsonify({'message': 'Customer created', 'customer_ID': new_customer.customer_ID}), 201

@app.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    return jsonify({'customer_ID': customer.customer_ID, 'customer_Other_Details': customer.customer_Other_Details}), 200

@app.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    data = request.get_json()
    if 'customer_Other_Details' in data:
        customer.customer_Other_Details = data['customer_Other_Details']

    db.session.commit()
    return jsonify({'message': 'Customer updated'}), 200

@app.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted'}), 200

@app.route('/customer_calls', methods=['POST'])
def create_call():
    data = request.get_json()
    required_fields = ['customer_ID', 'call_Date_Time', 'call_Outcome_Code', 'call_Status_Code']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing {field}'}), 400

    try:
        new_call = CustomerCall(
            customer_ID=data['customer_ID'],
            call_Date_Time=data['call_Date_Time'],
            call_Outcome_Code=data['call_Outcome_Code'],
            call_Status_Code=data['call_Status_Code']
        )
        db.session.add(new_call)
        db.session.commit()
    except IntegrityError:
        return jsonify({'error': 'Database integrity error'}), 500

    return jsonify({'message': 'Call logged', 'call_ID': new_call.call_ID}), 201

@app.route('/customer_calls/<int:call_id>', methods=['GET'])
def get_call(call_id):
    call = CustomerCall.query.get(call_id)
    if not call:
        return jsonify({'error': 'Call not found'}), 404

    return jsonify({
        'call_ID': call.call_ID,
        'customer_ID': call.customer_ID,
        'call_Date_Time': call.call_Date_Time,
        'call_Outcome_Code': call.call_Outcome_Code,
        'call_Status_Code': call.call_Status_Code
    }), 200

@app.route('/customer_calls/<int:call_id>', methods=['DELETE'])
def delete_call(call_id):
    call = CustomerCall.query.get(call_id)
    if not call:
        return jsonify({'error': 'Call not found'}), 404

    db.session.delete(call)
    db.session.commit()
    return jsonify({'message': 'Call deleted'}), 200

# --- Protected Endpoints --- 
@app.route('/protected', methods=['GET'])
@token_required
def protected():
    return jsonify({"message": f"Hello, {request.user['username']}!"}), 200

@app.route('/admin', methods=['GET'])
@token_required
@role_required("admin")
def admin_only():
    return jsonify({"message": "Welcome, Admin!"}), 200

# --- Error Handling --- 
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'An internal error occurred'}), 500

# --- Run the Application --- 
if __name__ == '__main__':
    app.run(debug=True)
