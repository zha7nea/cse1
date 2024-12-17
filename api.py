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