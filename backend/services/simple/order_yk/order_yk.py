# Order Microservice (order.py)
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:8889/order'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class MenuItem(db.Model):
    __tablename__ = 'menu'
    ID = db.Column(db.Integer, primary_key=True)
    restaurant_ID = db.Column(db.String(13), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)

    def json(self):
        return {
            "ID": self.ID,
            "restaurant_ID": self.restaurant_ID,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "is_available": self.is_available
        }

@app.route("/menu/<string:restaurant_id>")
def get_menu(restaurant_id):
    menu = MenuItem.query.filter_by(restaurant_ID=restaurant_id).all()
    return jsonify({"menu": [item.json() for item in menu]})

if __name__ == '__main__':
    app.run(port=5002, debug=True)

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
