@app.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)  # Use Session.get()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    return jsonify({'customer_ID': customer.customer_ID, 'customer_Other_Details': customer.customer_Other_Details}), 200

