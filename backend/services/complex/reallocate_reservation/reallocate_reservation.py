from flask import Flask, request, jsonify
import requests
import json
import pika
import rabbitmq.amqp_setup
import rabbitmq.amqp_lib
import sys, os

app = Flask(__name__)

# RabbitMQ Connection
def connectAMQP():
    global connection, channel
    try:
        connection, channel = rabbitmq.amqp_lib.connect(
            hostname=rabbitmq.amqp_setup.amqp_host,
            port=rabbitmq.amqp_setup.amqp_port,
            exchange_name=rabbitmq.amqp_setup.exchange_name,
            exchange_type=rabbitmq.amqp_setup.exchange_type,
        )
    except Exception as e:
        print(f"Failed to connect to RabbitMQ: {e}")
        sys.exit(1)

# Publish message to RabbitMQ
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

# retrieve
@app.route('/reallocate', methods=['POST'])
def reallocate_reservation():
    data = request.get_json()
    reservation_id = data.get("reservation_id")

    if not reservation_id:
        return jsonify({"error": "Missing reservation_id"}), 400

    #call for outsystem - Waitlist ms
    try:
        waitlist_response = requests.get("https://qks.outsystemscloud.com/Waitlist_Service/rest/waitlist/Get_nextUser")
        waitlist_response.raise_for_status()
        waitlist_data = waitlist_response.json()
        user_id = waitlist_data.get("user_id")
        if not user_id:
            return jsonify({"error": "No user found on waitlist"}), 404
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to get waitlist user: {str(e)}"}), 500

    #get user details from user ms
    try:
        user_response = requests.get(f"http://localhost:5004/user/details/{user_id}")
        user_response.raise_for_status()
        user_data = user_response.json()
        user_name = user_data.get("name")
        user_phone = user_data.get("phone")
        if not user_name or not user_phone:
            return jsonify({"error": "Incomplete user details"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to get user details: {str(e)}"}), 500

    #send the user_id to update the reservation status
    try:
        reservation_update_data = {
            "user_id": user_id,
            "status": "pending"
        }
        reservation_response = requests.patch(f"http://localhost:5001/reservation/reallocate/{reservation_id}", json=reservation_update_data)
        reservation_response.raise_for_status()
        reservation_data = reservation_response.json()
        
        table_no = reservation_data.get("table_no")
        if not table_no:
            return jsonify({"error": "Table number missing in reservation response"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to update reservation: {str(e)}"}), 500

    #queue the message into rabbitmq
    notification_data = {
        "user_name": user_name,
        "user_phone": user_phone,
        "table_no": table_no,
        "message_type": "reallocation.notice"
    }

    try:
        publish_message("reallocation.notice", notification_data)
        return jsonify({"message": "Reallocation successful", "status": "pending"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to send reallocation notification: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting reallocation_reservation service...")
    connectAMQP()
    app.run(host='0.0.0.0', port=5008, debug=True)
