from flask import Flask, request, jsonify
import requests
import json
import pika, rabbitmq.amqp_lib, time, rabbitmq.amqp_setup

app = Flask(__name__)

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

@app.route('/cancel-reservation', methods=['POST'])
def cancel_reservation():
    try:
        data = request.json
        
        if not data or 'reservation_id' not in data or 'payment_id' not in data:
            return jsonify({"error": "Missing reservation_id or payment_id"}), 400
        
        reservation_id = data['reservation_id']
        payment_id = data['payment_id']
        
        # Step 1: Get reservation details from reservation service
        reservation_response = requests.get(f"http://localhost:5002/api/reservations/{reservation_id}")
        if reservation_response.status_code != 200:
            return jsonify({"error": "Reservation not found"}), 404
        
        reservation_data = reservation_response.json()['data']
        user_id = reservation_data['user_id']
        
        # Step 2: Get user details from user service
        user_response = requests.get(f"http://localhost:5003/api/users/{user_id}")
        if user_response.status_code != 200:
            return jsonify({"error": "User not found"}), 404
        
        user_data = user_response.json()['data']
        refund_amount = reservation_data['price']
        
        # Step 3: Cancel the payment with Stripe
        stripe_response = requests.post(f"http://localhost:5004/api/stripe/cancel-payment/{payment_id}")
        if stripe_response.status_code != 200:
            return jsonify({"error": "Failed to cancel payment"}), 500
        
        # Step 4: Update reservation in reservation service
        update_response = requests.patch(
            f"http://localhost:5002/api/reservations/{reservation_id}",
            json={"status": "empty", "user_id": None, "count": None, "price": None}
        )
        
        if update_response.status_code != 200:
            return jsonify({"error": "Failed to update reservation"}), 500
        
        # Step 5: Send notification via RabbitMQ
        notification_data = {
            "reservation_id": reservation_id,
            "user_name": user_data['name'],
            "user_phone": user_data['phone'],
            "refund_amount": refund_amount,
            "message_type": "reservation.cancellation"
        }
        
        publish_message("reservation.cancellation", notification_data)
        
        # Step 6: Trigger reallocation
        reallocation_data = {"reservation_id": reservation_id}
        reallocation_response = requests.post("http://localhost:5005/reallocate", json=reallocation_data)
        
        if reallocation_response.status_code != 200:
            # Non-critical error, just log it
            print(f"Warning: Reallocation service returned status {reallocation_response.status_code}")
        
        return jsonify({
            "message": "Reservation cancelled successfully",
            "reservation_id": reservation_id,
            "payment_id": payment_id,
            "refund_amount": refund_amount
        }), 200
            
    except Exception as e:
        print(f"Error in cancel_reservation: {str(e)}")
        return jsonify({"error": f"Cancellation failed: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting cancel_booking service...")
    connectAMQP()
    app.run(host='0.0.0.0', port=5002, debug=True)
