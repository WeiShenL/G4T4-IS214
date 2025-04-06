import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, project_root)

import json
import time
import requests
from flask import Flask, request, jsonify
import pika

from backend.rabbitmq.amqp_lib import connect, is_connection_open
from backend.rabbitmq.amqp_setup import (
    amqp_host, 
    amqp_port, 
    exchange_name, 
    exchange_type
)

app = Flask(__name__)

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

@app.route('/reallocate', methods=['POST'])
def reallocate_reservation():
    try:
        data = request.get_json()
        reservation_id = data.get("reservation_id")

        if not reservation_id:
            return jsonify({"error": "Missing reservation_id"}), 400

        print(f"Starting reallocation process for reservation ID: {reservation_id}")

        # Call OutSystems waitlist service to get the next user in the waitlist
        try:
            print("Calling OutSystems Waitlist API to get next user...")
            waitlist_response = requests.get("https://qks.outsystemscloud.com/Waitlist_Service/rest/waitlist/Get_nextUser")
            waitlist_response.raise_for_status()
            waitlist_data = waitlist_response.json()
            user_id = waitlist_data.get("user_id")
            
            if not user_id:
                print("No users found in waitlist")
                return jsonify({"message": "No users in waitlist"}), 404
                
            print(f"Next user from waitlist: {user_id}")
        except requests.exceptions.RequestException as e:
            print(f"Error calling OutSystems Waitlist API: {str(e)}")
            return jsonify({"error": f"Failed to get waitlist user: {str(e)}"}), 500

        # Get user details from user service
        try:
            print(f"Getting user details for user ID: {user_id}")
            user_response = requests.get(f"http://localhost:5000/api/user/{user_id}")
            user_response.raise_for_status()
            user_data = user_response.json()
            
            if user_data.get("code") != 200:
                print(f"Error getting user data: {user_data}")
                return jsonify({"error": "Failed to get user details"}), 500
                
            user_details = user_data.get("data", {})
            user_name = user_details.get("customer_name", "Customer")
            user_phone = user_details.get("phone_number", "")
            
            print(f"Retrieved user details: {user_name}, {user_phone}")
            
            if not user_name or not user_phone:
                print("Incomplete user details")
                return jsonify({"error": "Incomplete user details"}), 500
        except requests.exceptions.RequestException as e:
            print(f"Error calling User API: {str(e)}")
            return jsonify({"error": f"Failed to get user details: {str(e)}"}), 500

        # Update the reservation with the new user ID
        try:
            print(f"Updating reservation {reservation_id} with new user ID: {user_id}")
            reservation_update_data = {
                "user_id": user_id,
                "status": "Pending"
            }
            reservation_response = requests.patch(
                f"http://localhost:5002/reservation/reallocate/{reservation_id}", 
                json=reservation_update_data
            )
            reservation_response.raise_for_status()
            reservation_data = reservation_response.json()
            
            print(f"Reservation update response: {reservation_data}")
            
            table_no = reservation_data.get("table_no")
            if not table_no:
                print("Table number missing in reservation response")
                return jsonify({"error": "Table number missing in reservation response"}), 500
        except requests.exceptions.RequestException as e:
            print(f"Error updating reservation: {str(e)}")
            return jsonify({"error": f"Failed to update reservation: {str(e)}"}), 500

        # Queue notification message to RabbitMQ
        try:
            print(f"Sending reallocation notice to user: {user_name}")
            notification_data = {
                "user_id": user_id,
                "user_name": user_name,
                "user_phone": user_phone,
                "table_no": table_no,
                "message_type": "reallocation.notice"
            }
            
            # Publish the notification message
            notification_sent = publish_message("reallocation.notice", notification_data)
            
            if notification_sent:
                print("Reallocation notification sent successfully")
                return jsonify({
                    "message": "Reallocation successful", 
                    "status": "pending",
                    "user_id": user_id,
                    "table_no": table_no
                }), 200
            else:
                print("Reallocation notification could not be sent")
                return jsonify({"error": "Failed to send reallocation notification"}), 500
        except Exception as e:
            print(f"Error sending notification: {str(e)}")
            return jsonify({"error": f"Failed to send reallocation notification: {str(e)}"}), 500
            
    except Exception as e:
        print(f"Unexpected error during reallocation: {str(e)}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting reallocation_reservation service...")
    connectAMQP()
    app.run(host='0.0.0.0', port=5009, debug=True)