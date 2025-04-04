import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, project_root)

import json
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import pika

from backend.rabbitmq.amqp_lib import connect, is_connection_open
from backend.rabbitmq.amqp_setup import (
    amqp_host, 
    amqp_port, 
    exchange_name, 
    exchange_type
)

app = Flask(__name__)
CORS(app)

connection = None
channel = None

# Connect to RabbitMQ
def connectAMQP():
    global connection, channel
    max_retries = 5
    for attempt in range(max_retries):
        try:
            if connection is None or not is_connection_open(connection):
                print("  Connecting to AMQP broker...")
                connection, channel = connect(
                    hostname=amqp_host,
                    port=amqp_port,
                    exchange_name=exchange_name,
                    exchange_type=exchange_type,
                )
            return
        except Exception as e:
            print(f"  Attempt {attempt+1}/{max_retries}: Unable to connect to RabbitMQ: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print("  Max retries reached, exiting...")
                exit(1)

# Publish message to RabbitMQ
def publish_message(routing_key, message):
    global connection, channel
    if connection is None or not is_connection_open(connection):
        connectAMQP()
    
    message_json = json.dumps(message)
    channel.basic_publish(
        exchange=exchange_name,
        routing_key=routing_key,
        body=message_json
    )
    print(f"  Published message to {routing_key}: {message_json}")

@app.route('/cancel/<int:reservation_id>', methods=['POST'])
def process_cancellation(reservation_id):
    # Call reservation.py to cancel the reservation
    try:
        # Use the reservation API endpoint in your application
        reservation_response = requests.patch(
            f"http://localhost:5002/api/reservation/cancel/{reservation_id}"
        )
        reservation_response.raise_for_status()
        reservation_data = reservation_response.json()
        print(f"Reservation data received: {reservation_data}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to cancel reservation: {str(e)}")
        return jsonify({"error": f"Failed to cancel reservation: {str(e)}"}), 500

    # Extract user_id, table_no, refund_amount, and order_id from the response
    user_id = reservation_data.get("user_id")
    table_no = reservation_data.get("table_no")
    refund_amount = reservation_data.get("refund_amount")
    payment_id = reservation_data.get("payment_id")
    order_id = reservation_data.get("order_id")  # Get order_id if available

    if not user_id:
        return jsonify({"error": "No user associated with this reservation"}), 404

    # Get user details from customer_profiles table
    try:
        # Using our user service
        user_response = requests.get(f"http://localhost:5000/api/user/{user_id}")
        user_response.raise_for_status()
        user_data = user_response.json()
        print(f"User data received: {user_data}")
        
        # Extract the user details we need
        user_name = user_data.get("data", {}).get("customer_name", "Customer")
        user_phone = user_data.get("data", {}).get("phone_number", "")
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch user details: {str(e)}")
        return jsonify({"error": f"Failed to fetch user details: {str(e)}"}), 500

    # Process refund if payment_id exists
    if payment_id:
        try:
            # Call the payment service to process the refund
            refund_response = requests.post(
                "http://localhost:5008/api/payment/refund",
                json={"payment_id": payment_id}
            )
            refund_response.raise_for_status()
            refund_data = refund_response.json()
            print(f"Refund processed: {refund_data}")
            
            # Delete the order associated with this order_id
            if order_id:
                # Delete by order_id if available (new method)
                delete_order_response = requests.delete(
                    f"http://localhost:5004/api/orders/{order_id}"
                )
                if delete_order_response.status_code == 200:
                    print(f"Order with ID {order_id} deleted successfully")
                else:
                    print(f"Failed to delete order or no order found with ID: {order_id}")
                
        except requests.exceptions.RequestException as e:
            print(f"Failed to process refund: {str(e)}")
            # Continue with cancellation even if refund fails
    
    # Queue a notification message to RabbitMQ
    try:
        notification_data = {
            "reservation_id": reservation_id,
            "user_id": user_id,
            "user_name": user_name,
            "user_phone": user_phone,
            "table_no": table_no,
            "refund_amount": refund_amount,
            "payment_id": payment_id,  # Include payment_id for the UI to process the refund
            "message_type": "reservation.cancellation"
        }
        
        publish_message("reservation.cancellation", notification_data)
        
        return jsonify({
            "message": "Reservation cancelled and notification sent.",
            "status": "cancelled",
            "reservation_id": reservation_id,
            "payment_id": payment_id  # Include payment_id in the response for the UI
        }), 200
    except Exception as e:
        print(f"Error triggering notification: {str(e)}")
        return jsonify({"error": f"Error triggering notification: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting cancel_booking service...")
    connectAMQP()
    app.run(host='0.0.0.0', port=5005, debug=True)