import os
import json
import threading
import pika
import time
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from twilio.rest import Client
from datetime import datetime
from supabase import create_client, Client as SupabaseClient

# Load environment variables
load_dotenv()

# RabbitMQ configuration
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", 5672))
RABBITMQ_EXCHANGE = "notification_topic"
RABBITMQ_EXCHANGE_TYPE = "topic"

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/api/notification/health", methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "notification-service",
        "timestamp": datetime.now().isoformat()
    }), 200
    
# Supabase configuration
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Message templates for different event types
MESSAGE_TEMPLATES = {
    #US1
    "reservation.confirmation": "Hi there {username}! Your reservation (ID: {reservation_id}) has been confirmed. See you soon!",
    "waitlist.notification": "Hi {username}! The restaurant {restaurant_name} is currently at full capacity. We've added you to the waitlist and will notify you when a table becomes available. Thank you for your patience!",

    #US2
    "reservation.cancellation": "Hi there {username}! Your reservation (ID: {reservation_id}) has been canceled and a refund of ${refund_amount} has been processed. We look forward to seeing you again! Thank you!",
    "reservation.reservation.decline": "Hi there {username}! You have declined the table offer for Table {table_no}. A refund of ${refund_amount} has been processed if applicable. Thank you!",
    "reallocation.notice": "Hi there {username}! Table {table_no} is currently open, would you like to book it? If so, please click on this link: http://localhost:5173 to start the booking process!",
    "reallocation.confirmation": "Hi {username}, your reservation (ID: {reservation_id}) for Table {table_no} has been confirmed for {booking_time}. Thank you!",
    
    #US3
    "delivery.order.confirmation": "Hi there {username}! Your order (ID: {order_id}) has been confirmed for delivery. Thank you for ordering with us!",
    "delivery.order.accepted": "Hi there {customer_name}! Your order (ID: {order_id}) has been assigned a driver, {driver_name}. Thank you for ordering with us!",
    "delivery.order.pickedup": "Good news {customer_name}! Your order (ID: {order_id}) has been picked up by your allocated driver. {driver_name} is on the way!",
    "delivery.order.delivered": "Hello {customer_name}! Your order (ID: {order_id}) has been delivered. Thank you for your purchase and we hope to see you soon!"
}

# Sends an SMS via Twilio
def send_sms(phone, message):
    try:
        # change to string
        phone_str = str(phone)
        
        # remove any funny characters
        digits_only = ''.join(char for char in phone_str if char.isdigit())
        
        # only digits
        if not digits_only:
            raise ValueError(f"Invalid phone number: {phone_str} contains no digits")
            
        # add back +
        formatted_phone = f"+{digits_only}"
            
        # send via Twilio
        sms = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=formatted_phone
        )
        
        logging.info(f"SMS sent successfully to {phone} (SID: {sms.sid})")
        return {"status": "success", "twilio_sid": sms.sid}
    except Exception as e:
        logging.error(f"Failed to send SMS to {phone}: {e}")
        return {"status": "failed", "error": str(e)}

# Save the notification to DB
def save_notification_to_db(message, msg_type, status):
    try:
        #Specify the data that is to be saved into DB
        notification_data = {
            "message": message,
            "status": status,
            "type": msg_type,
        }
        
        response = supabase.table('notification').insert(notification_data).execute()
        
        if not response.data:
            logging.error("Failed to save notification to Supabase")
        else:
            logging.info(f"Notification saved to Supabase: {response.data[0].get('id')}")
            
    except Exception as e:
        logging.error(f"Error saving notification to Supabase: {e}")

def rabbitmq_callback(ch, method, properties, body):
    try:
        logging.info(f"Received message: {body}")
        data = json.loads(body)
        
        msg_type = data.get("message_type")
        user_phone = data.get("user_phone")
        table_no = data.get("table_no", "N/A")
        username = data.get("user_name", "there")
        reservation_id = data.get("reservation_id", "N/A")
        refund_amount = data.get("refund_amount", "N/A")
        restaurant_name = data.get("restaurant_name", "The restaurant")
        booking_time = data.get("booking_time", "N/A")
        order_id= data.get("order_id", "N/A")

        driver_name = data.get("driver_name", "Driver") 
        customer_name = data.get("customer_name", "Customer") 
        
        # Format booking_time if available
        if booking_time != "N/A" and booking_time:
            try:
                booking_dt = datetime.fromisoformat(booking_time.replace('Z', '+00:00'))
                # Format as a readable date/time
                booking_time = booking_dt.strftime("%A, %B %d, %Y at %I:%M %p")
            except Exception as e:
                logging.warning(f"Could not format booking time: {e}")

        if not user_phone or not msg_type:
            logging.warning("Missing required fields in RabbitMQ message")
            return

        # Format the message based on the event type
        message_template = MESSAGE_TEMPLATES.get(msg_type, "Notification: {msg_type}")
        formatted_message = message_template.format(
            username=username,
            reservation_id=reservation_id,
            order_id= order_id,
            refund_amount=refund_amount,
            table_no=table_no,
            restaurant_name=restaurant_name,
            booking_time=booking_time,

            driver_name=driver_name,  
            customer_name=customer_name,  
        )

        logging.info(f"Processing {msg_type} event...")
        sms_result = send_sms(user_phone, formatted_message)

        # Save the notification to the database
        save_notification_to_db(formatted_message, msg_type, sms_result["status"] == "success")

        if sms_result["status"] == "success":
            logging.info(f"Notification sent successfully for {msg_type}")
        else:
            logging.error(f"Failed to send notification for {msg_type}: {sms_result.get('error')}")
    except Exception as e:
        logging.error(f"Error processing RabbitMQ message: {e}")

# Connect to RabbitMQ
def connect_to_rabbitmq():
    """Connect to RabbitMQ and return connection and channel"""
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                heartbeat=300,
                blocked_connection_timeout=300
            )
        )
        channel = connection.channel()
        
        # Ensure exchange exists
        channel.exchange_declare(
            exchange=RABBITMQ_EXCHANGE,
            exchange_type=RABBITMQ_EXCHANGE_TYPE,
            durable=True
        )
        
        return connection, channel
    except Exception as e:
        logging.error(f"Error connecting to RabbitMQ: {e}")
        return None, None

def start_rabbitmq_consumer():
    while True:
        try:
            logging.info("Connecting to RabbitMQ...")
            connection, channel = connect_to_rabbitmq()
            
            if not connection or not channel:
                logging.error("Failed to connect to RabbitMQ. Retrying in 5 seconds...")
                time.sleep(5)
                continue

            queues = {
                "Order_Confirmation": "order.confirmation",
                "Reservation_Confirmation": "reservation.confirmation",
                "Reservation_Cancellation": "reservation.cancellation",
                "Reservation_Decline": "reservation.reservation.decline",
                "Reallocation_Notice": "reallocation.notice",
                "Reallocation_Confirmation": "reallocation.confirmation",
                "Waitlist_Notification": "waitlist.notification",
                "Delivery_Order_Accepted" : "delivery.order.accepted",
                "Delivery_Order_Pickedup" : "delivery.order.pickedup",
                "Delivery_Order_Delivered" : "delivery.order.delivered",
                "Delivery_Order_Confirmation" : "delivery.order.confirmation"
            }

            for queue_name, routing_key in queues.items():
                logging.info(f"Consuming from queue: {queue_name}")
                channel.queue_declare(queue=queue_name, durable=True)
                channel.queue_bind(
                    exchange=RABBITMQ_EXCHANGE,
                    queue=queue_name,
                    routing_key=routing_key,
                )
                channel.basic_consume(
                    queue=queue_name,
                    on_message_callback=rabbitmq_callback,
                    auto_ack=True,
                )

            logging.info("Waiting for messages...")
            channel.start_consuming()
        except pika.exceptions.ConnectionClosedByBroker:
            logging.warning("Connection closed by broker. Reconnecting...")
            time.sleep(5)
            continue
        except KeyboardInterrupt:
            logging.info("Stopping RabbitMQ consumer...")
            break
        except Exception as e:
            logging.error(f"Unexpected error in RabbitMQ consumer: {e}")
            time.sleep(5)

if __name__ == '__main__':
    # Start RabbitMQ consumer in a separate thread
    threading.Thread(target=start_rabbitmq_consumer, daemon=True).start()
    port = int(os.environ.get('PORT', 5005))
    app.run(host='0.0.0.0', port=port, debug=True)