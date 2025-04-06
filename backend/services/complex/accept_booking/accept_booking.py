import sys
import os
import json
import requests
from flask import Flask, request, jsonify
import pika
import time
import uuid
import random
from flask_cors import CORS

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, project_root)

# Import RabbitMQ connection utilities
from backend.rabbitmq.amqp_lib import connect, is_connection_open
from backend.rabbitmq.amqp_setup import (
    amqp_host,
    amqp_port,
    exchange_name,
    exchange_type
)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global connection variables
connection = None
channel = None

# Connect to RabbitMQ
def connectAMQP():
    global connection, channel
    max_retries = 5
    for attempt in range(max_retries):
        try:
            if connection is None or not is_connection_open(connection):
                print("Connecting to AMQP broker...")
                connection, channel = connect(
                    hostname=amqp_host,
                    port=amqp_port,
                    exchange_name=exchange_name,
                    exchange_type=exchange_type,
                )
            return True
        except Exception as e:
            print(f"Attempt {attempt+1}/{max_retries}: Unable to connect to RabbitMQ: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print("Max retries reached, exiting...")
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

@app.route('/accept-booking', methods=['POST'])
def accept_booking():
    try:
        # Parse incoming JSON data
        data = request.get_json()
        print(f"Received data: {data}")

        # Extract required fields
        reservation_id = data.get("reservation_id")
        user_id = data.get("user_id")
        count = data.get("count")
        payment_id = data.get("payment_id")
        order_id = data.get("order_id")
        price = data.get("price")
        booking_time = data.get("booking_time")
        
        # Validate required fields
        if not all([reservation_id, user_id, count]):
            missing_fields = []
            for field in ['reservation_id', 'user_id', 'count']:
                if not data.get(field):
                    missing_fields.append(field)
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Step 1: Generate a new reservation ID if needed
        new_reservation_id = data.get("new_reservation_id", random.randrange(200, 999))

        # Step 2: Update Reservation Details via Reservation Service
        try:
            print(f"Updating reservation details for reservation ID: {reservation_id}")
            update_payload = {
                "new_reservation_id": new_reservation_id,
                "status": "Booked",
                "count": count,
                "price": price,
                "order_id": order_id,
                "payment_id": payment_id
            }
            
            # Add booking_time if provided
            if booking_time:
                update_payload["booking_time"] = booking_time
                print(f"Including booking_time in update: {booking_time}")
                
            # Update the reservation
            update_response = requests.patch(
                f"http://localhost:5002/reservation/reallocate_confirm_booking/{reservation_id}",
                json=update_payload
            )
            update_response.raise_for_status()
            updated_data = update_response.json()
            table_no = updated_data.get("table_no")
            
            # Use the booking_time from the response if available
            if updated_data.get("booking_time"):
                booking_time = updated_data.get("booking_time")
                print(f"Using booking_time from response: {booking_time}")

            if not table_no:
                return jsonify({"error": "Table number missing in reservation response"}), 500
        except requests.exceptions.RequestException as e:
            print(f"Error updating reservation: {str(e)}")
            return jsonify({"error": f"Failed to update reservation: {str(e)}"}), 500

        # Step 3: Get user details - either from the request data or fetch from User Service
        username = data.get("username")
        phone_number = data.get("phone_number")
        
        # If user details not provided in request, fetch from User Service
        if not username or not phone_number:
            try:
                print(f"Fetching user details for user ID: {user_id}")
                user_response = requests.get(f"http://localhost:5000/api/user/{user_id}")
                user_response.raise_for_status()
                user_data = user_response.json()

                if user_data.get("code") != 200:
                    print(f"Error getting user data: {user_data}")
                    return jsonify({"error": "Failed to get user details"}), 500

                username = user_data.get("data", {}).get("customer_name", "Customer")
                phone_number = user_data.get("data", {}).get("phone_number", "")
            except requests.exceptions.RequestException as e:
                print(f"Error fetching user details: {str(e)}")
                return jsonify({"error": f"Failed to fetch user details: {str(e)}"}), 500

        # Step 4: Queue Notification Message to RabbitMQ
        try:
            print(f"Queueing notification for user: {username}")
            notification_data = {
                "user_name": username,
                "user_phone": phone_number,
                "table_no": table_no,
                "booking_time": booking_time,
                "reservation_id": new_reservation_id,
                "message_type": "reallocation.confirmation"
            }
            publish_message("reallocation.confirmation", notification_data)
            print("Notification queued successfully")
        except Exception as e:
            print(f"Error queuing notification: {str(e)}")
            return jsonify({"error": f"Failed to queue notification: {str(e)}"}), 500

        # Return success response with the new reservation ID
        return jsonify({
            "message": "Booking accepted and reservation updated successfully",
            "reservation_id": new_reservation_id,  
            "user_id": user_id,
            "username": username,
            "phone_number": phone_number,
            "table_no": table_no,
            "status": "Booked",
            "booking_time": booking_time
        }), 200

    except Exception as e:
        print(f"Unexpected error during booking acceptance: {str(e)}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting accept_booking service...")
    connectAMQP()
    app.run(host='0.0.0.0', port=5010, debug=True)