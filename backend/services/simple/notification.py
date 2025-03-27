import os, json, threading, pika, rabbitmq.amqp_setup, rabbitmq.amqp_lib, time, logging
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from twilio.rest import Client
from datetime import datetime

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI2')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Twilio & RabbitMQ configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Notification model
class Notification(db.Model):
    __tablename__ = 'notification'
    notification_id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(999), nullable=False)
    status = db.Column(db.Boolean, default=False)  # True if sent, False if failed
    type = db.Column(db.String(999), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)

# Message templates for different event types
MESSAGE_TEMPLATES = {
    "reservation.cancellation": "Hi there {username}! Your reservation for {reservation_id} has been canceled and a refund of {refund_amount} has been processed. We look forward to seeing you again! Thank you!",
    "order.confirmation": "Your order has been confirmed. Thank you for dining with us!",
    "reservation.confirmation": "Your reservation for {reservation_id} has been confirmed. See you soon!",
    "reallocation.notice": "Hi there {username}! Table {table_no} is currently open, would you like to book it? If so, please tap on the SMS to start the booking process...",
    "reallocation.confirmation": "Table {table_no} booking has been confirmed. Thank you!"
}

#Sends an SMS via Twilio
def send_sms(phone, message):
    try:
        sms = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone
        )
        logging.info(f"SMS sent successfully to {phone} (SID: {sms.sid})")
        return {"status": "success", "twilio_sid": sms.sid}
    except Exception as e:
        logging.error(f"Failed to send SMS to {phone}: {e}")
        return {"status": "failed", "error": str(e)}

#Save the notification to the database 
def save_notification_to_db(message, msg_type, status):
    new_notification = Notification(
        message=message,
        status=status,
        type=msg_type
    )
    db.session.add(new_notification)
    db.session.commit()

def rabbitmq_callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        msg_type = data.get("message_type")
        user_phone = data.get("user_phone")
        username = data.get("user_name", "there")  #return there as the name if name is empty
        reservation_id = data.get("reservation_id", "N/A") #return NA if id is empty
        refund_amount = data.get("refund_amount", "N/A") #return NA if amount is empty

        if not user_phone or not msg_type:
            print("Missing required fields in RabbitMQ message")
            return

        # Format the message based on the event type
        message_template = MESSAGE_TEMPLATES.get(msg_type, "Notification: {msg_type}")
        formatted_message = message_template.format(
            username=username,
            reservation_id=reservation_id,
            refund_amount=refund_amount,
            new_table_no=data.get("new_table_no", "N/A")
        )

        print(f"Processing {msg_type} event...")
        sms_result = send_sms(user_phone, formatted_message)

        # Save the notification to the database
        save_notification_to_db(formatted_message, msg_type, status=(sms_result["status"] == "success"))

        if sms_result["status"] == "success":
            print(f"Notification sent successfully for {msg_type}")
        else:
            print(f"Failed to send notification for {msg_type}: {sms_result['error']}")
    except Exception as e:
        print(f"Error processing RabbitMQ message: {e}")

def start_rabbitmq_consumer():
    while True:
        try:
            print("Connecting to RabbitMQ...")
            connection, channel = rabbitmq.amqp_lib.connect(
                hostname=rabbitmq.amqp_setup.amqp_host,
                port=rabbitmq.amqp_setup.amqp_port,
                exchange_name=rabbitmq.amqp_setup.exchange_name,
                exchange_type=rabbitmq.amqp_setup.exchange_type,
            )

            queues = {
                "Order_Confirmation": "order.confirmation",
                "Reservation_Confirmation": "reservation.confirmation",
                "Reservation_Cancellation": "reservation.cancellation",
                "Reallocation_Notice": "reallocation.notice",
                "Reallocation_Confirmation": "reallocation.confirmation",
            }

            for queue_name, routing_key in queues.items():
                print(f"Consuming from queue: {queue_name}")
                channel.queue_declare(queue=queue_name, durable=True)
                channel.queue_bind(
                    exchange=rabbitmq.amqp_setup.exchange_name,
                    queue=queue_name,
                    routing_key=routing_key,
                )
                channel.basic_consume(
                    queue=queue_name,
                    on_message_callback=rabbitmq_callback,
                    auto_ack=True,
                )

            print("Waiting for messages...")
            channel.start_consuming()
        except pika.exceptions.ConnectionClosedByBroker:
            print("Connection closed by broker. Reconnecting...")
            continue
        except KeyboardInterrupt:
            print("Stopping RabbitMQ consumer...")
            break
        except Exception as e:
            print(f"Unexpected error in RabbitMQ consumer: {e}")
            time.sleep(5)

# Health check route
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Notification service running"}), 200

if __name__ == '__main__':
    # Start RabbitMQ consumer in a separate thread
    threading.Thread(target=start_rabbitmq_consumer, daemon=True).start()
    app.run(host='0.0.0.0', port=5003, debug=True)