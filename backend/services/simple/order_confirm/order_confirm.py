# order_confirm.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import stripe
import pika

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:8889/order'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

stripe.api_key = 'sk_test_your_test_key_here'  # Replace with your actual Stripe key

db = SQLAlchemy(app)

class Order(db.Model):
    __tablename__ = 'order_table'
    order_id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')

@app.route('/order/confirm', methods=['POST'])
def confirm_order():
    data = request.get_json()
    order_id = data['order_id']
    token = data['stripe_token']  # Frontend will generate Stripe token

    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"message": "Order not found."}), 404

    try:
        stripe.Charge.create(
            amount=int(order.total_amount * 100),
            currency='sgd',
            description=f"Payment for Order ID {order_id}",
            source=token
        )
        order.status = 'confirmed'
        db.session.commit()

        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='notification')

        message = f"Reservation {order.reservation_id} confirmed. Payment of ${order.total_amount:.2f} received."
        channel.basic_publish(exchange='', routing_key='notification', body=message)
        connection.close()

        return jsonify({"message": "Order confirmed and payment successful."})

    except Exception as e:
        return jsonify({"message": "Payment failed.", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5003, debug=True)
