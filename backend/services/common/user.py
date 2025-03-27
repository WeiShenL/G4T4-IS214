from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from db import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI2')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


#User Model
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(999), nullable=False)
    phoneNo = db.Column(db.Integer, nullable=False)
    homeAddress = db.Column(db.String(999), nullable=False)
    postalCode = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(999), nullable=False)
    password = db.Column(db.String(999), nullable=False)

    reservations = db.relationship('Reservation', back_populates='user')