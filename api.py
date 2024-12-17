from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt
from sqlalchemy.exc import IntegrityError

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/callcenter'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to a more secure secret

    if config:
        app.config.update(config)

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()

    register_routes(app)
    register_error_handlers(app)

    return app

# Register routes
def register_routes(app):
    @app.route('/')
    def home():
        return jsonify({
            'message': 'Call Center Management System',
            'endpoints': {
                '/customers': 'Manage accounts',
                '/customers/<int:customer_ID>': 'Manage a specific account'
            }
        })
    
    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()

        # Assume we check user credentials here
        username = data.get('username')
        password = data.get('password')

        # In a real app, you would validate the user against the database
        if username == 'admin' and password == 'admin':
            access_token = create_access_token(identity=username, additional_claims={'role': 'admin'})
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

    @app.route('/customers', methods=['GET'])
    @jwt_required()
    def get_customers():
        claims = get_jwt()  # Get the full claims from the JWT
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Access forbidden: You do not have the required role'}), 403

        customers = Customer.query.all()
        return jsonify([{
            'customer_id': c.customer_id,  
            'customer_other_details': c.customer_other_details 
        } for c in customers])
    
    @app.route('/customers/<int:customer_ID>', methods=['GET'])
    @jwt_required()  # Ensure the request includes a valid JWT
    def get_customer(customer_ID):
        claims = get_jwt()  # Get the full claims from the JWT

        if claims.get('role') != 'admin':
            return jsonify({'error': 'Access forbidden: You do not have the required role'}), 403

        customer = db.session.get(Customer, customer_ID)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404

        # Return the account data
        return jsonify({
            'customer_id': customer.customer_id,  
            'customer_other_details': customer.customer_other_details 
        })

    @app.route('/customer_calls', methods=['GET'])
    @jwt_required()
    def get_customer_calls():
        claims = get_jwt()  # Get the full claims from the JWT
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Access forbidden: You do not have the required role'}), 403

        customer_calls = CustomerCall.query.all()
        return jsonify([{
            'call_id': cc.call_id,  # Customer Call ID
            'customer_id': cc.customer_id,  # Customer ID associated with the call
            'call_date_time': cc.call_date_time,  # Date and time of the call
            'call_description': cc.call_description,  # Description of the call
            'call_outcome_code': cc.call_outcome_code,  # Outcome code of the call
            'call_status_code': cc.call_status_code  # Status code of the call
        } for cc in customer_calls])

    @app.route('/customers', methods=['POST'])
    def create_customer():
        data = request.get_json()

        # List of required fields (excluding auto-incremented customer_id)
        required_fields = ['customer_other_details']  # Adjust this list based on your model

        # Check if any required field is missing
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing field(s): {", ".join(missing_fields)}'}), 400

        try:
            # Create a new customer instance without specifying customer_id (auto-increment)
            new_customer = Customer(
                customer_other_details=data['customer_other_details']  # Only other details
            )
            db.session.add(new_customer)
            db.session.commit()
            return jsonify({'message': 'Customer created successfully'}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'Database integrity error'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 400
        
    @app.route('/customer_calls', methods=['POST'])
    def create_customer_call():
        data = request.get_json()

        # List of required fields (excluding auto-incremented call_id)
        required_fields = ['customer_id', 'call_date_time', 'call_description', 'call_outcome_code', 'call_status_code']

        # Check if any required field is missing
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing field(s): {", ".join(missing_fields)}'}), 400

        try:
            # Create a new CustomerCall instance without specifying call_id (auto-increment)
            new_customer_call = CustomerCall(
                customer_id=data['customer_id'],
                call_date_time=data['call_date_time'],
                call_description=data['call_description'],
                call_outcome_code=data['call_outcome_code'],
                call_status_code=data['call_status_code'],
                # Optionally include other fields like call_Outcome_Code or call_Status_Code if provided
            )
            db.session.add(new_customer_call)
            db.session.commit()
            return jsonify({'message': 'Customer call created successfully'}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'Database integrity error'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 400
        
    @app.route('/customers/<int:customer_id>', methods=['DELETE'])
    def delete_customer(customer_id):
        try:
            # Find the customer by ID
            customer = db.session.get(Customer, customer_id)
            
            if customer is None:
                return jsonify({'error': 'Customer not found'}), 404

            # Deleting associated CustomerCalls (if any)
            customer_calls = CustomerCall.query.filter_by(customer_id=customer_id).all()
            for call in customer_calls:
                db.session.delete(call)

            # Now delete the customer
            db.session.delete(customer)
            db.session.commit()
            return jsonify({'message': 'Customer and associated calls deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @app.route('/customers/<int:customer_id>', methods=['PUT'])
    def update_customer(customer_id):
        data = request.get_json()

        # Find the customer by ID
        customer = db.session.get(Customer, customer_id)
        
        if customer is None:
            return jsonify({'error': 'Customer not found'}), 404

        # Check if the customer_other_details field is provided
        if 'customer_other_details' in data:
            customer.customer_other_details = data['customer_other_details']
        else:
            return jsonify({'error': 'customer_other_details field is required'}), 400

        try:
            # Commit the changes to the database
            db.session.commit()
            
            # Return a success message
            return jsonify({'message': 'Customer information updated successfully'}), 200
        except Exception as e:
            db.session.rollback()  # Rollback if there is any exception
            return jsonify({'error': str(e)}), 400


    

# Register error handlers
def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Internal server error'}), 500


class Customer(db.Model):
    __tablename__ = 'customers'

    customer_id = db.Column('customer_ID', db.Integer, primary_key=True, autoincrement=True)
    customer_other_details = db.Column('customer_Other_Details', db.String(255), nullable=True)

class RefCallOutcome(db.Model):
    __tablename__ = 'ref_call_outcome'

    call_outcome_code = db.Column('call_Outcome_Code', db.String(50), primary_key=True)
    call_outcome_description = db.Column('call_Outcome_Description', db.String(255), nullable=True)

class RefCallStatus(db.Model):
    __tablename__ = 'ref_call_status'

    call_status_code = db.Column('call_Status_Code', db.String(50), primary_key=True)
    call_status_description = db.Column('call_Status_Description', db.String(255), nullable=True)

class CustomerCall(db.Model):
    __tablename__ = 'customer_calls'

    call_id = db.Column('call_ID', db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column('customer_ID', db.Integer, db.ForeignKey('customers.customer_ID'), nullable=False)
    call_date_time = db.Column('call_Date_Time', db.DateTime, nullable=True)
    call_description = db.Column('call_Description', db.String(255), nullable=True)
    call_outcome_code = db.Column('call_Outcome_Code', db.String(50), db.ForeignKey('ref_call_outcome.call_Outcome_Code'), nullable=True)
    call_status_code = db.Column('call_Status_Code', db.String(50), db.ForeignKey('ref_call_status.call_Status_Code'), nullable=True)

    # Relationships
    customer = db.relationship('Customer', backref='calls')
    call_outcome = db.relationship('RefCallOutcome', backref='calls')
    call_status = db.relationship('RefCallStatus', backref='calls')

class RefBusinessSector(db.Model):
    __tablename__ = 'ref_business_sector'

    business_sector_id = db.Column('business_Sector_ID', db.Integer, primary_key=True, autoincrement=True)
    business_sector_code = db.Column('business_Sector_Code', db.String(50), nullable=False)
    business_sector_description = db.Column('business_Sector_Description', db.String(255), nullable=True)

class RefCustomerType(db.Model):
    __tablename__ = 'ref_customer_type'

    customer_type_code = db.Column('customer_Type_Code', db.String(50), primary_key=True)
    customer_type_description = db.Column('customer_Type_Description', db.String(255), nullable=True)

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)