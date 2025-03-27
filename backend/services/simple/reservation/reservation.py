# do you want to make aa http get, passing userid and retrieving all users's orders, then when clicking a restaurant order, a modal shows up?
# or split it up, do http get 2 times, pass userid once retrieve all user orders, then when click restauant order, makes another http get based on the reservationid?

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime

app = Flask(__name__)
CORS(app)  
# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:3306/reservation'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class Reservation(db.Model):
    __tablename__ = 'reservation'
    reservation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    restaurant_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    table_no = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(999), nullable=False)
    count = db.Column(db.Integer, default=10)
    price = db.Column(db.Float, nullable=True)
    time = db.Column(db.TIMESTAMP, nullable=True)

    def json(self):
        return {
            "reservation_id": self.reservation_id,
            "restaurant_id": self.restaurant_id,
            "user_id": self.user_id,
            "table_no": self.table_no,
            "status": self.status,
            "count": self.count,
            "price": self.price,
            "time": self.time.isoformat() if self.time else None
        }

# retrieve all reservations
@app.route("/api/reservations", methods=['GET'])
def get_all_reservations():
    try:
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
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

# retrieve reservation using id
@app.route("/api/reservations/<int:reservation_id>", methods=['GET'])
def get_reservation(reservation_id):
    try:
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
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

# create a new reservation
@app.route("/api/reservations", methods=['POST'])
def create_reservation():
    try:
        data = request.get_json()
        
        # validation 
        required_fields = ['restaurant_id', 'status', 'count']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "code": 400,
                    "message": f"Missing required field: {field}"
                }), 400
        
        # create new reservation
        new_reservation = Reservation(
            restaurant_id=data['restaurant_id'],
            user_id=data.get('user_id'),
            table_no=data.get('table_no'),
            status=data['status'],
            count=data['count'],
            price=data.get('price'),
            time=datetime.fromisoformat(data['time']) if 'time' in data and data['time'] else datetime.now()
        )
        
        db.session.add(new_reservation)
        db.session.commit()
        
        return jsonify({
            "code": 201,
            "message": "Reservation created successfully.",
            "data": new_reservation.json()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

# get reservations by user_id
@app.route("/api/reservations/user/<int:user_id>", methods=['GET'])
def get_user_reservations(user_id):
    try:
        reservations = db.session.scalars(
            db.select(Reservation).filter_by(user_id=user_id)
        ).all()
        
        if reservations:
            return jsonify({
                "code": 200,
                "data": {
                    "reservations": [reservation.json() for reservation in reservations]
                }
            })
        return jsonify({
            "code": 404,
            "message": f"No reservations found for user: {user_id}"
        }), 404
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)