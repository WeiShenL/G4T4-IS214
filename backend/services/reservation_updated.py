import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timezone
from dotenv import load_dotenv
from common.db import db

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Reservation Model
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

# Retrieve Reservation by ID
@app.route('/reservation/<int:reservation_id>', methods=['GET'])
def get_reservation(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
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

# Cancel Reservation
@app.route('/reservation/cancel/<int:reservation_id>', methods=['PATCH'])
def cancel_reservation(reservation_id):
    reservation = Reservation.query.get(reservation_id)

    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    refund_amount = reservation.price if reservation.price else 0
    table_no = reservation.table_no
    user_id= reservation.user_id

    try:
        reservation.user_id = None
        reservation.status = "empty"
        reservation.count = None
        reservation.price = None
        reservation.time = None
        db.session.commit()
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Database update failed", "details": str(e)}), 500

    return jsonify({
        "reservation_id": reservation.reservation_id,
        "user_id": user_id,
        "table_no": table_no,
        "refund_amount": refund_amount
    }), 200

# Reallocate Reservation
@app.route('/reservation/reallocate/<int:reservation_id>', methods=['PATCH'])
def update_reservation(reservation_id):
    data = request.get_json()
    reservation = Reservation.query.get(reservation_id)

    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    if "user_id" in data:
        reservation.user_id = data["user_id"]
    if "status" in data:
        reservation.status = data["status"]

    db.session.commit()

    return jsonify({
        "reservation_id": reservation.reservation_id,
        "user_id": reservation.user_id,
        "table_no": reservation.table_no,
        "status": reservation.status
    }), 200

if __name__ == '__main__':
    print("Starting reservation service...")
    app.run(host='0.0.0.0', port=5001, debug=True)
