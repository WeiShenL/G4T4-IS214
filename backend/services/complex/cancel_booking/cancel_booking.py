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

# RabbitMQ configuration
RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
RABBITMQ_EXCHANGE = "notification_topic"
RABBITMQ_EXCHANGE_TYPE = "topic"

app = Flask(__name__)
CORS(app)

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

@app.route('/cancel/<int:reservation_id>', methods=['POST'])
def process_cancellation(reservation_id):
    # Call reservation.py to cancel the reservation
    # this clears the reservation fields, nullify fields
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
    restaurant_id= reservation_data.get("restaurant_id")
    refund_amount = reservation_data.get("refund_amount")
    payment_id = reservation_data.get("payment_id")
    order_id = reservation_data.get("order_id")  

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

    # TODO:Process refund if payment_id exists (exist where?) exit from reservation table as above?
    # i call the payment msc
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
    
    # Queue a notification message to RabbitMQ and trigger reallocation
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
        
        publish_to_rabbitmq("reservation.cancellation", notification_data)
        
        # Trigger reallocation
        reallocation_data = {"reservation_id": reservation_id, "restaurant_id": restaurant_id}
        requests.post("http://localhost:5009/reallocate", json=reallocation_data)
        
        return jsonify({
            "message": "Reservation cancelled and notification sent, and reallocation triggered.",
            "status": "cancelled",
            "reservation_id": reservation_id,
            "payment_id": payment_id  
        }), 200
    except Exception as e:
        print(f"Error triggering notification: {str(e)}")
        return jsonify({"error": f"Error triggering notification or reallocation: {str(e)}"}), 500
    
if __name__ == '__main__':
    print("Starting cancel_booking service...")
    app.run(host='0.0.0.0', port=5005, debug=True)