from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:8889/reservation'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class Reservation(db.Model):
    __tablename__ = 'reservation'
    reservation_id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.String(13), db.ForeignKey('restaurant.restaurant_id'), nullable=False)
    customer_name = db.Column(db.String(64), nullable=False)
    reservation_date = db.Column(db.Date, nullable=False)
    reservation_time = db.Column(db.Time, nullable=False)
    party_size = db.Column(db.Integer, nullable=False)

    def __init__(self, restaurant_id, customer_name, reservation_date, reservation_time, party_size):
        self.restaurant_id = restaurant_id
        self.customer_name = customer_name
        self.reservation_date = reservation_date
        self.reservation_time = reservation_time
        self.party_size = party_size

    def json(self):
        return {
            "reservation_id": self.reservation_id,
            "restaurant_id": self.restaurant_id,
            "customer_name": self.customer_name,
            "reservation_date": self.reservation_date.isoformat(),
            "reservation_time": self.reservation_time.isoformat(),
            "party_size": self.party_size
        }

@app.route("/reservation")
def get_all_reservations():
    reservation_list = db.session.scalars(db.select(Reservation)).all()
    if reservation_list:
        return jsonify({
            "code": 200,
            "data": {
                "reservations": [reservation.json() for reservation in reservation_list]
            }
        })
    return jsonify({
        "code": 404,
        "message": "No reservations found."
    }), 404

@app.route("/reservation/<int:reservation_id>")
def find_by_reservation_id(reservation_id):
    reservation = db.session.scalar(
        db.select(Reservation).filter_by(reservation_id=reservation_id)
    )
    if reservation:
        return jsonify({
            "code": 200,
            "data": reservation.json()
        })
    return jsonify({
        "code": 404,
        "message": "Reservation not found."
    }), 404

@app.route("/reservation", methods=['POST'])
def create_reservation():
    data = request.get_json()
    reservation = Reservation(
        restaurant_id=data['restaurant_id'],
        customer_name=data['customer_name'],
        reservation_date=datetime.strptime(data['reservation_date'], '%Y-%m-%d').date(),
        reservation_time=datetime.strptime(data['reservation_time'], '%H:%M').time(),
        party_size=data['party_size']
    )

    try:
        db.session.add(reservation)
        db.session.commit()
    except:
        return jsonify({
            "code": 500,
            "message": "An error occurred creating the reservation."
        }), 500

    return jsonify({
        "code": 201,
        "data": reservation.json()
    }), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
