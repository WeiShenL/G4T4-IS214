# when capacity of restaurant is full, then post a request to waitlist msc at outsystems as "user_id"
# user go thru payment process also, then order row fills up.


# create order, row order db 

# aft create order, if (count how many reservations based on that res ID)
# more than capacity instead submit user_id to the waitlist instead of creating reservation


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

# order create first, once success 200 then call reservation

@app.route('/create', methods=['POST'])
def call_create_reservation():
    try:
        # Get request data
        data = request.json
        
        # Validate required fields for reservation
        required_fields = ['restaurant_id', 'user_id', 'count', 'time', 'payment_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Add status if not provided
        if 'status' not in data:
            data['status'] = 'Booked'
        
        # Call reservation service to create the reservation
        print(f"Creating reservation with data: {data}")
        reservation_response = requests.post(
            "http://localhost:5002/api/reservations",
            json=data
        )
        
        if not reservation_response.ok:
            error_data = reservation_response.json()
            return jsonify({"error": f"Failed to create reservation: {error_data.get('message', reservation_response.status_code)}"}), reservation_response.status_code
        
        # Get the created reservation details
        reservation_data = reservation_response.json()
        print(f"Reservation created: {reservation_data}")
        
        # Get the reservation ID from the response
        reservation_id = reservation_data.get("data", {}).get("reservation_id")
        if not reservation_id:
            return jsonify({"error": "Reservation ID not found in response"}), 500
        
        # Get user details from user service
        user_id = data.get("user_id")
        try:
            user_response = requests.get(f"http://localhost:5000/api/user/{user_id}")
            user_response.raise_for_status()
            user_data = user_response.json()
            
            # Extract the user details we need
            user_name = user_data.get("data", {}).get("customer_name", "Customer")
            user_phone = user_data.get("data", {}).get("phone_number", "")
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch user details: {str(e)}")
            # Continue even if user details can't be fetched
            user_name = "Customer"
            user_phone = ""
        
        # Get restaurant details
        restaurant_id = data.get("restaurant_id")
        try:
            restaurant_response = requests.get(f"http://localhost:5001/api/restaurants/{restaurant_id}")
            restaurant_response.raise_for_status()
            restaurant_data = restaurant_response.json()
            
            # Extract restaurant name
            restaurant_name = restaurant_data.get("data", {}).get("name", f"Restaurant #{restaurant_id}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch restaurant details: {str(e)}")
            # Continue even if restaurant details can't be fetched
            restaurant_name = f"Restaurant #{restaurant_id}"
        
        # Queue a confirmation message to RabbitMQ
        try:
            notification_data = {
                "reservation_id": reservation_id,
                "user_id": user_id,
                "user_name": user_name,
                "user_phone": user_phone,
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant_name,
                "table_no": data.get("table_no", "TBD"),
                "time": data.get("time"),
                "count": data.get("count"),
                "payment_id": data.get("payment_id"),
                "message_type": "reservation.confirmation"
            }
            
            publish_message("reservation.confirmation", notification_data)
            
            # Return success response with reservation data
            return jsonify({
                "message": "Reservation created and confirmation notification sent.",
                "status": "booked",
                "reservation_id": reservation_id,
                "data": reservation_data.get("data", {})
            }), 201
            
        except Exception as e:
            print(f"Error triggering notification: {str(e)}")
            # Return partial success if only the notification fails
            return jsonify({
                "message": "Reservation created but confirmation notification failed.",
                "error": str(e),
                "status": "booked",
                "reservation_id": reservation_id,
                "data": reservation_data.get("data", {})
            }), 207
            
    except Exception as e:
        print(f"Error creating reservation: {str(e)}")
        return jsonify({"error": f"Error creating reservation: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting create_booking service...")
    connectAMQP()
    app.run(host='0.0.0.0', port=5006, debug=True)