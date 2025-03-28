from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:8889/restaurant'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class Restaurant(db.Model):
    __tablename__ = 'restaurant'
    restaurant_id = db.Column(db.String(13), primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    cuisine = db.Column(db.String(64), nullable=False)
    rating = db.Column(db.Float(precision=1), nullable=False)
    price_range = db.Column(db.String(5), nullable=False)

    def __init__(self, restaurant_id, name, cuisine, rating, price_range):
        self.restaurant_id = restaurant_id
        self.name = name
        self.cuisine = cuisine
        self.rating = rating
        self.price_range = price_range

    def json(self):
        return {
            "restaurant_id": self.restaurant_id,
            "name": self.name,
            "cuisine": self.cuisine,
            "rating": self.rating,
            "price_range": self.price_range
        }

@app.route("/restaurant")
def get_all():
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

@app.route("/restaurant/<string:restaurant_id>")
def find_by_restaurant_id(restaurant_id):
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

@app.route("/restaurant", methods=['POST'])
def create_restaurant():
    data = request.get_json()
    restaurant_id = data.get('restaurant_id')
    
    if db.session.scalar(db.select(Restaurant).filter_by(restaurant_id=restaurant_id)):
        return jsonify({
            "code": 400,
            "data": {"restaurant_id": restaurant_id},
            "message": "Restaurant already exists."
        }), 400

    restaurant = Restaurant(
        restaurant_id=restaurant_id,
        name=data['name'],
        cuisine=data['cuisine'],
        rating=data['rating'],
        price_range=data['price_range']
    )

    try:
        db.session.add(restaurant)
        db.session.commit()
    except:
        return jsonify({
            "code": 500,
            "data": {"restaurant_id": restaurant_id},
            "message": "An error occurred creating the restaurant."
        }), 500

    return jsonify({
        "code": 201,
        "data": restaurant.json()
    }), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
