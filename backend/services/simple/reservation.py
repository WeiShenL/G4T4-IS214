import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from common.db import db
from common.user import User


load_dotenv()

app = Flask(__name__)
CORS(app)

#Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

#Reservation Model
class Reservation(db.Model):
    __tablename__ = 'reservation'
    reservation_id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    table_no = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(999), nullable=False)
    count = db.Column(db.Integer, nullable=True)
    price = db.Column(db.Float(precision=2), nullable=True)
    time = db.Column(db.DateTime, nullable=True)
    user = db.relationship('User', back_populates='reservations', foreign_keys=[user_id])
    restaurant = db.relationship('Restaurant', back_populates='reservations', foreign_keys=[restaurant_id])

#Retrieving of specific reservation via id
@app.route('/reservation/<int:reservation_id>', methods=['GET'])
def get_reservation(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    if reservation is None:
        return jsonify({"message": "Reservation not found"}), 404
    return jsonify({
        "reservation_id": reservation.reservation_id,
        "restaurant_id": reservation.restaurant_id,
        "user_id": reservation.user_id,
        "table_no": reservation.table_no,
        "status": reservation.status,
        "count": reservation.count,
        "price": reservation.price,
        "time": reservation.time.isoformat() if reservation.time else "N/A"
    })

if __name__ == '__main__':
    print("Starting reservation service...")
    app.run(host='0.0.0.0', port=5001, debug=True)