@app.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)  # Use Session.get()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    return jsonify({'customer_ID': customer.customer_ID, 'customer_Other_Details': customer.customer_Other_Details}), 200

@app.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)  # Use Session.get()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    data = request.get_json()
    if 'customer_Other_Details' in data:
        customer.customer_Other_Details = data['customer_Other_Details']

    db.session.commit()
    return jsonify({'message': 'Customer updated'}), 200
