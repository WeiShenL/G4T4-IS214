# Composite Microservice with Routing Key
from flask import Flask, request, jsonify
import requests
import pika

app = Flask(__name__)

@app.route('/booking', methods=['POST'])
def make_booking():
    data = request.get_json()
    restaurant_id = data['restaurant_id']
    reservation_id = data['reservation_id']
    items = data['items']  # List of dicts: {"item_id": ..., "quantity": ...}
    customer_name = data.get('customer_name', 'A customer')

    # Get menu items for validation (optional)
    menu_res = requests.get(f'http://localhost:5002/menu/{restaurant_id}')
    if menu_res.status_code != 200:
        return jsonify({"error": "Menu service failed"}), 500

    menu = menu_res.json().get('menu', [])
    if not menu:
        return jsonify({"error": "No menu found for this restaurant"}), 404

    # Place the order via Order microservice
    order_payload = {
        "reservation_id": reservation_id,
        "items": items
    }
    order_res = requests.post('http://localhost:5002/order', json=order_payload)

    if order_res.status_code != 200:
        return jsonify({"error": "Order creation failed"}), 500

    order_data = order_res.json()

    # Send booking confirmation via RabbitMQ with routing key
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange='notification_topic', exchange_type='topic')

        msg = (
            f"New booking by {customer_name}!\n"
            f"Reservation ID: {reservation_id}, Order ID: {order_data['order_id']}, Total: ${order_data['total']}"
        )

        # Use a topic-based routing key like 'booking.notify.sms'
        channel.basic_publish(
            exchange='notification_topic',
            routing_key='booking.notify.sms',
            body=msg.encode('utf-8')
        )
        connection.close()

    except Exception as e:
        return jsonify({"message": "Order placed, but notification failed", "error": str(e)}), 207

    return jsonify({
        "message": "Booking successful",
        "order": order_data
    }), 201

if __name__ == '__main__':
    app.run(port=5005, debug=True)
