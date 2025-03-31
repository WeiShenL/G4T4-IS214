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
    #Call reservation.py to cancel the reservation
    try:
        reservation_response = requests.patch(
            f"http://localhost:5001/reservation/cancel/{reservation_id}"
        )
        reservation_response.raise_for_status()
        reservation_data = reservation_response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to cancel reservation: {str(e)}"}), 500

    # Extracted user_id, table_no, and refund_amount from the response of reservtion cancellation
    user_id = reservation_data.get("user_id")
    table_no = reservation_data.get("table_no")
    refund_amount = reservation_data.get("refund_amount")

    if not user_id:
        return jsonify({"error": "No user associated with this reservation"}), 404

    #Call user.py to get user details
    try:
        user_response = requests.get(f"http://localhost:5004/user/details/{user_id}")
        user_response.raise_for_status()
        user_data = user_response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch user details: {str(e)}"}), 500

    #Queue a notification message to RabbitMQ
    try:
        notification_data = {
            "reservation_id": reservation_id,
            "user_id": user_id,
            "user_name": user_data["name"],
            "user_phone": user_data["phone"],
            "table_no": table_no,
            "refund_amount": refund_amount,
            "message_type": "reservation.cancellation"
        }
        publish_message("reservation.cancellation", notification_data)

        # Step 4: Trigger reallocation
        reallocation_data = {"reservation_id": reservation_id}
        requests.post("http://localhost:5005/reallocate", json=reallocation_data)
        
        return jsonify({
            "message": "Reservation cancelled, notification sent, and reallocation triggered.",
            "status": "empty",
            "reservation_id": reservation_id
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error triggering notification or reallocation: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting cancel_booking service...")
    connectAMQP()
    app.run(host='0.0.0.0', port=5005, debug=True)