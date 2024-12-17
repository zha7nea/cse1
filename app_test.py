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