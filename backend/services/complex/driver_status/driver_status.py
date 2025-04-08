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

@app.route("/accept-order", methods=['POST'])
def accept_order():
    try:
        # Parse input
        data = request.json
        driver_id = data.get("driver_id")
        order_id = data.get("order_id")

        if not driver_id or not order_id:
            return jsonify({"code": 400, "message": "Missing driver_id or order_id."}), 400

        # Update Driver Availability
        driver_response = requests.patch(
            f"http://localhost:5012/driverdetails/{driver_id}",
            json={"availability": False}
        )
        if driver_response.status_code != 200:
            return jsonify({"code": 500, "message": "Failed to update driver availability."}), 500
        
        # Fetch driver profile to get driver information
        driver_profile_response = requests.get(f"http://localhost:5011/driver/{driver_id}")
        if driver_profile_response.status_code != 200:
            return jsonify({"code": 500, "message": "Failed to fetch driver profile."}), 500

        driver_data = driver_profile_response.json().get("data", {})
        driver_name = driver_data.get("driver_name", "Driver")  # Use the correct key for driver name

        # Fetch Order Details
        order_response = requests.get(f"http://localhost:5004/api/orders/{order_id}")
        if order_response.status_code != 200:
            return jsonify({"code": 404, "message": "Order not found."}), 404

        order_data = order_response.json().get("data", {})
        customer_id = order_data.get("user_id")
     

        # Fetch Customer Details
        customer_response = requests.get(f"http://localhost:5000/api/user/{customer_id}")
        if customer_response.status_code != 200:
            return jsonify({"code": 500, "message": "Failed to fetch customer details."}), 500

        customer_data = customer_response.json().get("data", {})
        customer_phone = customer_data.get("phone_number", None)
        customer_name = customer_data.get("customer_name", "Customer")  # Use the correct key for customer name

        # Publish Message to RabbitMQ
        message = {
            "order_id": order_id,
            "customer_id": customer_id,
            "user_phone": customer_phone,
            "driver_id": driver_id,
            "driver_name": driver_name,
            "customer_name": customer_name,
            "message_type": "delivery.order.accepted",
        }
        publish_message("delivery.order.accepted", message)

        # Return success response
        return jsonify({"code": 200, "message": "Order accepted successfully."}), 200

    except Exception as e:
        print(f"Error accepting order: {str(e)}")
        return jsonify({"code": 500, "message": "An error occurred while accepting the order."}), 500
    
    
@app.route("/pick-up-order", methods=['POST'])
def pick_up_order():
    try:
        # Parse input
        data = request.json
        driver_id = data.get("driver_id")
        order_id = data.get("order_id")

        if not driver_id or not order_id:
            return jsonify({"code": 400, "message": "Missing driver_id or order_id."}), 400
        
        # Fetch driver profile to get driver information
        driver_profile_response = requests.get(f"http://localhost:5011/driver/{driver_id}")
        if driver_profile_response.status_code != 200:
            return jsonify({"code": 500, "message": "Failed to fetch driver profile."}), 500

        driver_data = driver_profile_response.json().get("data", {})
        driver_name = driver_data.get("driver_name", "Driver")  # Use the correct key for driver name

        # Fetch Order Details
        order_response = requests.get(f"http://localhost:5004/api/orders/{order_id}")
        if order_response.status_code != 200:
            return jsonify({"code": 404, "message": "Order not found."}), 404

        order_data = order_response.json().get("data", {})
        customer_id = order_data.get("user_id")
     

        # Fetch Customer Details
        customer_response = requests.get(f"http://localhost:5000/api/user/{customer_id}")
        if customer_response.status_code != 200:
            return jsonify({"code": 500, "message": "Failed to fetch customer details."}), 500

        customer_data = customer_response.json().get("data", {})
        customer_phone = customer_data.get("phone_number", None)
        customer_name = customer_data.get("customer_name", "Customer")  # Use the correct key for customer name

        # Publish Message to RabbitMQ
        message = {
            "order_id": order_id,
            "customer_id": customer_id,
            "user_phone": customer_phone,
            "driver_id": driver_id,
            "driver_name": driver_name,
            "customer_name": customer_name,
            "message_type": "delivery.order.pickedup",
        }
        publish_message("delivery.order.pickedup", message)

        # Return success response
        return jsonify({"code": 200, "message": "Order pickedup successfully."}), 200

    except Exception as e:
        print(f"Error accepting order: {str(e)}")
        return jsonify({"code": 500, "message": "An error occurred while picking up the order."}), 500
    
    

@app.route("/deliver-order", methods=['POST'])
def deliver_order():
    try:
        # Parse input
        data = request.json
        driver_id = data.get("driver_id")
        order_id = data.get("order_id")

        if not driver_id or not order_id:
            return jsonify({"code": 400, "message": "Missing driver_id or order_id."}), 400

        # Update Driver Availability
        driver_response = requests.patch(
            f"http://localhost:5012/driverdetails/{driver_id}",
            json={"availability": True}
        )
        if driver_response.status_code != 200:
            return jsonify({"code": 500, "message": "Failed to update driver availability."}), 500
        
        # Fetch driver profile to get driver information
        driver_profile_response = requests.get(f"http://localhost:5011/driver/{driver_id}")
        if driver_profile_response.status_code != 200:
            return jsonify({"code": 500, "message": "Failed to fetch driver profile."}), 500

        driver_data = driver_profile_response.json().get("data", {})
        driver_name = driver_data.get("driver_name", "Driver")  # Use the correct key for driver name

        # Fetch Order Details
        order_response = requests.get(f"http://localhost:5004/api/orders/{order_id}")
        if order_response.status_code != 200:
            return jsonify({"code": 404, "message": "Order not found."}), 404

        order_data = order_response.json().get("data", {})
        customer_id = order_data.get("user_id")
     

        # Fetch Customer Details
        customer_response = requests.get(f"http://localhost:5000/api/user/{customer_id}")
        if customer_response.status_code != 200:
            return jsonify({"code": 500, "message": "Failed to fetch customer details."}), 500

        customer_data = customer_response.json().get("data", {})
        customer_phone = customer_data.get("phone_number", None)
        customer_name = customer_data.get("customer_name", "Customer")  # Use the correct key for customer name

        # Publish Message to RabbitMQ
        message = {
            "order_id": order_id,
            "customer_id": customer_id,
            "user_phone": customer_phone,
            "driver_id": driver_id,
            "driver_name": driver_name,
            "customer_name": customer_name,
            "message_type": "delivery.order.delivered",
        }
        publish_message("delivery.order.delivered", message)

        # Return success response
        return jsonify({"code": 200, "message": "Order delivered successfully."}), 200

    except Exception as e:
        print(f"Error delivering order: {str(e)}")
        return jsonify({"code": 500, "message": "An error occurred while delivering the order."}), 500
    
if __name__ == '__main__':
    print("Starting Driverstatus Service...")
    app.run(host='0.0.0.0', port=5101, debug=True)
