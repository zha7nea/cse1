from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from security import token_required, role_required, hash_password, login_user

app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@127.0.0.1/callcenterdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

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
    db.create_all()  # This creates all the tables defined in the models

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

    return jsonify({"message": "User registered successfully"}),

# --- Login Route --- 
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    response, status_code = login_user(data, User)
    return jsonify(response), status_code




# Create all tables in the database
with app.app_context():
    db.create_all()  # This creates all the tables defined in the models

 
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

# 
# --- Run the Application --- 
if __name__ == '__main__':
    app.run(debug=True)
