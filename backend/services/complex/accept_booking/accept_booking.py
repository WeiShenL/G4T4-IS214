import json
import requests
from flask import Flask, request, jsonify
import pika
import time
import uuid
import random
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# RabbitMQ configuration
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", 5672))
RABBITMQ_EXCHANGE = "notification_topic"
RABBITMQ_EXCHANGE_TYPE = "topic"

# Service URLs
USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://user-service:5000")
RESERVATION_SERVICE_URL = os.environ.get("RESERVATION_SERVICE_URL", "http://reservation-service:5000")
ORDER_SERVICE_URL = os.environ.get("ORDER_SERVICE_URL", "http://order-service:5000")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Publish message to RabbitMQ
def publish_to_rabbitmq(routing_key, message):
    """Publish a message to RabbitMQ"""
    try:
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT
            )
        )
        channel = connection.channel()
        
        # Ensure exchange exists
        channel.exchange_declare(
            exchange=RABBITMQ_EXCHANGE,
            exchange_type=RABBITMQ_EXCHANGE_TYPE,
            durable=True
        )
        
        # Publish message
        channel.basic_publish(
            exchange=RABBITMQ_EXCHANGE,
            routing_key=routing_key,
            body=json.dumps(message)
        )
        
        # Close connection
        connection.close()
        print(f"Published message to {routing_key}: {json.dumps(message)}")
        return True
    except Exception as e:
        print(f"Error publishing to RabbitMQ: {e}")
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

        # Generate a new reservation ID if needed
        new_reservation_id = data.get("new_reservation_id", random.randrange(200, 999))

        # Update Reservation Details via Reservation Service
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
                
            # Update the reservation by calling the reservation.py service
            update_response = requests.patch(
                f"{RESERVATION_SERVICE_URL}/reservation/reallocate_confirm_booking/{reservation_id}",
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

        # Update Order Type from "dine_in(pending)" to "dine_in"
        try:
            if order_id:
                print(f"Updating order type for order ID: {order_id}")
                order_update_payload = {
                    "order_type": "dine_in"
                }
                order_update_response = requests.patch(
                    f"{ORDER_SERVICE_URL}/api/orders/{order_id}/type",
                    json=order_update_payload
                )
                order_update_response.raise_for_status()
                print(f"Order type updated successfully for order ID: {order_id}")
            else:
                print("No order_id provided, skipping order type update")
        except requests.exceptions.RequestException as e:
            print(f"Error updating order type: {str(e)}")
            return jsonify({"error": f"Failed to update order type: {str(e)}"}), 500

        # Get user details from User Service
        username = data.get("username")
        phone_number = data.get("phone_number")
        
        # If user details not provided in request, fetch from User Service
        if not username or not phone_number:
            try:
                print(f"Fetching user details for user ID: {user_id}")
                user_response = requests.get(f"{USER_SERVICE_URL}/api/user/{user_id}")
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

        # Queue Notification Message to RabbitMQ
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
            publish_to_rabbitmq("reallocation.confirmation", notification_data)
            print("Notification queued successfully")
            
            # Return success response
            return jsonify({
                "message": "Booking accepted and confirmed",
                "reservation_id": new_reservation_id,
                "table_no": table_no,
                "booking_time": booking_time
            }), 200
        
        except Exception as e:
            print(f"Error queueing notification: {str(e)}")
            # Return partial success since the booking was accepted
            return jsonify({
                "message": "Booking accepted but notification failed",
                "reservation_id": new_reservation_id,
                "table_no": table_no,
                "booking_time": booking_time
            }), 207

    except Exception as e:
        print(f"Error in accept_booking: {str(e)}")
        return jsonify({"error": f"Error processing booking acceptance: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5010))
    print(f"Starting accept_booking service on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)