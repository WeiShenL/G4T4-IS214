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
def create_booking():
    try:
        # Get request data (TODO: receives json string from the UI?)
        data = request.json
        
        # Validate required fields for the combined order and reservation
        required_fields = [
            'restaurant_id', 'user_id', 'count', 'time', 'payment_id',
            'item_name', 'quantity', 'order_price'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # first create the order
        order_data = {
            "user_id": data['user_id'],
            "restaurant_id": data['restaurant_id'],
            "item_name": data['item_name'],
            "quantity": data['quantity'],
            "order_price": data['order_price'],
            "payment_id": data['payment_id'],
            "order_type": data.get('order_type', 'dine_in')
        }
        
        # Call order service to create the order
        print(f"Creating order with data: {order_data}")
        order_response = requests.post(
            "http://localhost:5004/api/orders",
            json=order_data
        )
        
        if not order_response.ok:
            error_data = order_response.json()
            return jsonify({
                "error": f"Failed to create order: {error_data.get('message', order_response.status_code)}"
            }), order_response.status_code
        
        # Get the created order details
        order_data = order_response.json()
        print(f"Order created: {order_data}")
        
        # Get the order ID from the response
        order_id = order_data.get("data", {}).get("order_id")
        if not order_id:
            return jsonify({"error": "Order ID not found in response"}), 500
        
        # create the reservation with the order_id
        reservation_data = {
            "restaurant_id": data['restaurant_id'],
            "user_id": data['user_id'],
            "table_no": data.get('table_no'),
            "status": data.get('status', 'Booked'),
            "count": data['count'],
            "price": data['order_price'],
            "time": data['time'],
            "order_id": order_id,
            "payment_id": data['payment_id']
        }
        
        # Call reservation service
        print(f"Creating reservation with data: {reservation_data}")
        reservation_response = requests.post(
            "http://localhost:5002/api/reservations",
            json=reservation_data
        )
        
        if not reservation_response.ok:
            error_data = reservation_response.json()
            return jsonify({
                "error": f"Failed to create reservation: {error_data.get('message', reservation_response.status_code)}"
            }), reservation_response.status_code
        
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
                "message": "Booking created and confirmation notification sent.",
                "status": "booked",
                "order_id": order_id,
                "reservation_id": reservation_id,
                "data": {
                    "order": order_data.get("data", {}),
                    "reservation": reservation_data.get("data", {})
                }
            }), 201
            
        except Exception as e:
            print(f"Error triggering notification: {str(e)}")
            # Return partial success if only the notification fails
            return jsonify({
                "message": "Booking created but confirmation notification failed.",
                "error": str(e),
                "status": "booked",
                "order_id": order_id,
                "reservation_id": reservation_id,
                "data": {
                    "order": order_data.get("data", {}),
                    "reservation": reservation_data.get("data", {})
                }
            }), 207
            
    except Exception as e:
        print(f"Error creating booking: {str(e)}")
        return jsonify({"error": f"Error creating booking: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting create_booking service...")
    connectAMQP()
    app.run(host='0.0.0.0', port=5006, debug=True)