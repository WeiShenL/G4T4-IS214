from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timezone
from simple.reservation import Reservation
from common.user import User
from common.db import db
import sys, os, json, pika, rabbitmq.amqp_lib, time, requests, rabbitmq.amqp_setup

app = Flask(__name__)
CORS(app)

db.init_app(app)

connection = None
channel = None

# connection to rabbit MQ
def connectAMQP():
    global connection, channel
    max_retries = 5
    for attempt in range(max_retries):
        try:
            if connection is None or not rabbitmq.amqp_lib.is_connection_open(connection):
                print("  Connecting to AMQP broker...")
                connection, channel = rabbitmq.amqp_lib.connect(
                    hostname=rabbitmq.amqp_setup.amqp_host,
                    port=rabbitmq.amqp_setup.amqp_port,
                    exchange_name=rabbitmq.amqp_setup.exchange_name,
                    exchange_type=rabbitmq.amqp_setup.exchange_type,
                )
            return
        except Exception as e:
            print(f"  Attempt {attempt+1}/{max_retries}: Unable to connect to RabbitMQ: {e}")
            if attempt < max_retries - 1:
                time.sleep(2) 
            else:
                print("  Max retries reached, exiting...")
                exit(1)

# send message to rabbitmq for queuing
def publish_message(routing_key, message):
    if connection is None or not rabbitmq.amqp_lib.is_connection_open(connection):
        connectAMQP()
    
    message_json = json.dumps(message)
    rabbitmq.amqp_setup.channel.basic_publish(
        exchange=rabbitmq.amqp_setup.exchange_name,
        routing_key=routing_key,
        body=message_json
    )
    print(f"  Published message to {routing_key}: {message_json}")

@app.route('/reservation/<int:reservation_id>', methods=['PATCH'])
def update_reservation(reservation_id):
    #Updates the reservation and triggers a notification + reallocation
    reservation = Reservation.query.get(reservation_id)
    if reservation is None:
        return jsonify({"message": "Reservation not found"}), 404
    
    user = User.query.get(reservation.user_id)
    if user is None:
        return jsonify({"message": "User not found"}), 404
    
    refund_amount = reservation.price

    try:
        # Update reservation details
        reservation.user_id = None
        reservation.status = 'empty'
        reservation.count = None
        reservation.price = None
        reservation.time = datetime.now(timezone.utc)

        db.session.commit()
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Database update failed", "details": str(e)}), 500
    
    # data that is to be sent to rabbitmq
    notification_data = {
        "reservation_id": reservation_id,
        "user_name": user.name,
        "user_phone": user.phone,
        "refund_amount": refund_amount,
        "message_type": "reservation.cancellation"
    }

    try:
        publish_message("reservation.cancellation", notification_data)

        # Trigger reallocation
        reallocation_data = {"reservation_id": reservation_id}
        requests.post("http://localhost:5004/reallocate", json=reallocation_data)

        return jsonify({
            "message": "Reservation cancelled, notification sent, and reallocation triggered.",
            "status": reservation.status,
            "reservation_id": reservation_id
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error triggering notification or reallocation: {str(e)}"}), 505

if __name__ == '__main__':
    print("Starting cancel_booking service...")
    connectAMQP()
    app.run(host='0.0.0.0', port=5002, debug=True)
