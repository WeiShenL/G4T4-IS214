# Notification Microservice (notification.py)
import pika
import time

def start_notification_listener():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='notification')

    def callback(ch, method, properties, body):
        print("[Notification] Sending SMS/Email:", body.decode())

    channel.basic_consume(queue='notification', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    start_notification_listener()