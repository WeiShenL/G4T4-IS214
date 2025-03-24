from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ

app = Flask(__name__)
CORS(app)  
# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:3306/reservation'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class Restaurant(db.Model):
    __tablename__ = 'restaurant'
    restaurant_id = db.Column(db.Integer, primary_key=True)
    capacity = db.Column(db.Integer, nullable=False)
    availability = db.Column(db.Boolean, nullable=False)
    name = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(999), nullable=False)
    rating = db.Column(db.String(999), nullable=False)
    cuisine = db.Column(db.String(999), nullable=False)

    def json(self):
        return {
            "restaurant_id": self.restaurant_id,
            "capacity": self.capacity,
            "availability": self.availability,
            "name": self.name,
            "address": self.address,
            "rating": self.rating,
            "cuisine": self.cuisine
        }

# retrieve all restaurants
@app.route("/api/restaurants", methods=['GET'])
def get_all_restaurants():
    try:
        restaurant_list = db.session.scalars(db.select(Restaurant)).all()
        if restaurant_list:
            return jsonify({
                "code": 200,
                "data": {
                    "restaurants": [restaurant.json() for restaurant in restaurant_list]
                }
            })
        return jsonify({
            "code": 404,
            "message": "No restaurants found."
        }), 404
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

# retrieve restaurant using id
@app.route("/api/restaurants/<int:restaurant_id>", methods=['GET'])
def get_restaurant(restaurant_id):
    try:
        restaurant = db.session.scalar(
            db.select(Restaurant).filter_by(restaurant_id=restaurant_id)
        )
        if restaurant:
            return jsonify({
                "code": 200,
                "data": restaurant.json()
            })
        return jsonify({
            "code": 404,
            "message": "Restaurant not found."
        }), 404
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

# create rest, might not need?
@app.route("/api/restaurants", methods=['POST'])
def create_restaurant():
    try:
        data = request.get_json()
        
        # validation 
        required_fields = ['name', 'cuisine', 'capacity', 'address', 'rating']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "code": 400,
                    "message": f"Missing required field: {field}"
                }), 400
        
        # name unique
        existing_restaurant = db.session.scalar(
            db.select(Restaurant).filter_by(name=data['name'])
        )
        if existing_restaurant:
            return jsonify({
                "code": 400,
                "message": "Restaurant with this name already exists."
            }), 400
        
        # create new restaurant
        new_restaurant = Restaurant(
            name=data['name'],
            cuisine=data['cuisine'],
            capacity=data['capacity'],
            address=data['address'],
            rating=data['rating'],
            availability=data.get('availability', True)  
        )
        
        db.session.add(new_restaurant)
        db.session.commit()
        
        return jsonify({
            "code": 201,
            "message": "Restaurant created successfully.",
            "data": new_restaurant.json()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

# filter restaurants by cuisine
@app.route("/api/restaurants/cuisine/<string:cuisine>", methods=['GET'])
def get_restaurants_by_cuisine(cuisine):
    try:
        restaurants = db.session.scalars(
            db.select(Restaurant).filter_by(cuisine=cuisine)
        ).all()
        
        if restaurants:
            return jsonify({
                "code": 200,
                "data": {
                    "restaurants": [restaurant.json() for restaurant in restaurants]
                }
            })
        return jsonify({
            "code": 404,
            "message": f"No restaurants found with cuisine: {cuisine}"
        }), 404
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

# check if open 1 = open 0 = close
@app.route("/api/restaurants/availability/<int:availability>", methods=['GET'])
def get_restaurants_by_availability(availability):
    try:
        restaurants = db.session.scalars(
            db.select(Restaurant).filter_by(availability=availability)
        ).all()
        
        if restaurants:
            return jsonify({
                "code": 200,
                "data": {
                    "restaurants": [restaurant.json() for restaurant in restaurants]
                }
            })
        else:
            return jsonify({
                "code": 404,
                "message": "No restaurants found with this availability status"
            }), 404
            
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)