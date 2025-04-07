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
from datetime import datetime

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
            return True
        except Exception as e:
            print(f"  Attempt {attempt+1}/{max_retries}: Unable to connect to RabbitMQ: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print("  Max retries reached, continuing operation...")
                return False

# Publish message to RabbitMQ
def publish_message(routing_key, message):
    global connection, channel
    
    # Try up to 3 times to publish the message
    for attempt in range(3):
        try:
            # Check connection and try to reconnect if needed
            if connection is None or not is_connection_open(connection):
                connected = connectAMQP()
                if not connected:
                    print("  Could not connect to RabbitMQ, will try again...")
                    time.sleep(1)
                    continue
            
            message_json = json.dumps(message)
            channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=message_json
            )
            print(f"  Published message to {routing_key}: {message_json}")
            return True
        except Exception as e:
            print(f"  Error publishing message (attempt {attempt+1}/3): {e}")
            connection = None  # Reset connection to force reconnect
            time.sleep(1)
    
    print("  Failed to publish message after multiple attempts")
    return False

# order create first, once success 200 then call reservation
@app.route('/create', methods=['POST'])
def create_booking():
    try:
        # Get request data
        data = request.json
        
        # Validate required fields for the combined order and reservation
        required_fields = [
            'restaurant_id', 'user_id', 'count', 'time', 'payment_id',
            'item_name', 'quantity', 'order_price'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # First create the order with order_type as "dine_in(pending)"
        order_data = {
            "user_id": data['user_id'],
            "restaurant_id": data['restaurant_id'],
            "item_name": data['item_name'],
            "quantity": data['quantity'],
            "order_price": data['order_price'],
            "payment_id": data['payment_id'],
            "order_type": "dine_in(pending)"  # Initially set as pending
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
            
        # Get restaurant capacity and current reservations
        restaurant_id = data['restaurant_id']
        print(f"Checking capacity for restaurant {restaurant_id}")
        capacity_response = requests.get(
            f"http://localhost:5001/api/restaurants/capacity/{restaurant_id}"
        )
        
        if not capacity_response.ok:
            error_data = capacity_response.json()
            return jsonify({
                "error": f"Failed to check restaurant capacity: {error_data.get('message', capacity_response.status_code)}"
            }), capacity_response.status_code
            
        capacity_data = capacity_response.json()
        restaurant_capacity = capacity_data.get("data", {}).get("capacity", 0)
        
        # We need to count only dine-in orders against capacity
        # First, get all orders with order_type = "dine_in" for this restaurant
        dine_in_orders_response = requests.get(
            f"http://localhost:5004/api/orders/restaurant/{restaurant_id}/type/dine_in"
        )
        
        dine_in_count = 0
        if dine_in_orders_response.ok:
            orders_data = dine_in_orders_response.json()
            dine_in_orders = orders_data.get("data", {}).get("orders", [])
            dine_in_count = len(dine_in_orders)
        else:
            print(f"Warning: Failed to retrieve dine-in orders: {dine_in_orders_response.text}")
        
        # Use dine_in_count instead of current_reservations
        current_reservations = dine_in_count
        available_slots = max(0, restaurant_capacity - current_reservations)
        
        print(f"Restaurant capacity: {restaurant_capacity}, Current dine-in reservations: {current_reservations}")
        
        # Get user details for notifications
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
        try:
            restaurant_response = requests.get(f"http://localhost:5001/api/restaurants/{restaurant_id}")
            restaurant_response.raise_for_status()
            restaurant_data = restaurant_response.json()
            
            # Extract restaurant name
            restaurant_name = restaurant_data.get("data", {}).get("name", f"Restaurant #{restaurant_id}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch restaurant details: {str(e)}")
            restaurant_name = f"Restaurant #{restaurant_id}"
            
        # Check if restaurant is at capacity
        if current_reservations >= restaurant_capacity:
            print(f"Restaurant at capacity. Adding user to waitlist.")
            
            # Add user to waitlist via OutSystems API
            current_time = datetime.now().isoformat()
            waitlist_data = {
                "user_id": user_id,
                "time": current_time
            }
            
            try:
                waitlist_response = requests.post(
                    "https://qks.outsystemscloud.com/Waitlist_Service/rest/waitlist/addUser",
                    json=waitlist_data
                )
                
                # Queue waitlist notification to RabbitMQ
                notification_data = {
                    "user_id": user_id,
                    "user_name": user_name,
                    "user_phone": user_phone,
                    "restaurant_id": restaurant_id,
                    "restaurant_name": restaurant_name,
                    "time": data.get("time"),
                    "count": data.get("count"),
                    "payment_id": data.get("payment_id"),
                    "order_id": order_id,
                    "message_type": "waitlist.notification"
                }
                
                publish_message("waitlist.notification", notification_data)
                
                # Return response indicating waitlist status
                return jsonify({
                    "message": "Restaurant is at capacity. You have been added to the waitlist.",
                    "status": "waitlisted",
                    "order_id": order_id,
                    "data": {
                        "order": order_data.get("data", {})
                    }
                }), 200
                
            except Exception as e:
                print(f"Error adding to waitlist: {str(e)}")
                return jsonify({
                    "error": f"Failed to add to waitlist: {str(e)}"
                }), 500
        
        # If we reach here, there's capacity available, create the reservation
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
        
        # Update order type to "dine_in"
        order_update_response = requests.patch(
            f"http://localhost:5004/api/orders/{order_id}/type",
            json={"order_type": "dine_in"}
        )
        
        if not order_update_response.ok:
            print(f"Warning: Failed to update order type: {order_update_response.text}")
        
        # Get the reservation ID from the response
        reservation_id = reservation_data.get("data", {}).get("reservation_id")
        if not reservation_id:
            return jsonify({"error": "Reservation ID not found in response"}), 500
        
        # Queue a confirmation message to RabbitMQ
        try:
            notification_data = {
                "reservation_id": reservation_id,
                "user_id": user_id,
                "user_name": user_name,
                "user_phone": user_phone,
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant_name,
                "table_no": reservation_data.get("data", {}).get("table_no", "TBD"),
                "time": data.get("time"),
                "count": data.get("count"),
                "payment_id": data.get("payment_id"),
                "message_type": "reservation.confirmation"
            }
            
            notification_sent = publish_message("reservation.confirmation", notification_data)
            
            status_message = "Booking created and confirmation notification sent."
            status_code = 201
            
            if not notification_sent:
                status_message = "Booking created but notification could not be sent (RabbitMQ issue)."
                status_code = 207  # Partial success
            
            # Return response with appropriate message
            return jsonify({
                "message": status_message,
                "status": "booked",
                "order_id": order_id,
                "reservation_id": reservation_id,
                "data": {
                    "order": order_data.get("data", {}),
                    "reservation": reservation_data.get("data", {})
                }
            }), status_code
            
        except Exception as e:
            print(f"Error in notification handling: {str(e)}")
            # Return partial success since the booking was created
            return jsonify({
                "message": "Booking created but notification could not be sent.",
                "status": "booked",
                "order_id": order_id,
                "reservation_id": reservation_id,
                "data": {
                    "order": order_data.get("data", {}),
                    "reservation": reservation_data.get("data", {})
                }
            }), 207
    
    except Exception as e:
        print(f"Error in create_booking: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting create_booking service...")
    connectAMQP()
    app.run(host='0.0.0.0', port=5006, debug=True)