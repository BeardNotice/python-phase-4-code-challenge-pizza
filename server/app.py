#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/restaurants", methods=["GET"])
def restaurants():
    restaurants = [
        {key: value for key, value in restaurant.to_dict().items() if key != 'restaurant_pizzas'}
        for restaurant in Restaurant.query.all()
        ]

    return make_response(restaurants, 200)

@app.route("/restaurants/<int:id>", methods=["GET", "DELETE"])
def restaurants_by_id(id):
    restaurant = Restaurant.query.filter(Restaurant.id==id).first()
    if not restaurant:
        return make_response({"error": "Restaurant not found"}, 404)
    if request.method == "GET":
        return make_response(restaurant.to_dict(), 200)

    elif request.method == "DELETE":

        db.session.delete(restaurant)
        db.session.commit()

        return make_response("", 204)

@app.route("/pizzas", methods=["GET"])
def pizzas():
    pizzas = [pizza.to_dict() for pizza in Pizza.query.all()]

    return make_response(pizzas, 200)

@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizzas():
    data = request.get_json()
    if not data:
        return make_response({"errors": "No input data provided"}, 400)
    try:
        price = data.get("price")
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")
        new_restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
    except ValueError as e:
        return make_response({"errors": ["validation errors"]}, 400)

    db.session.add(new_restaurant_pizza)
    db.session.commit()

    return make_response(new_restaurant_pizza.to_dict(), 201)

if __name__ == "__main__":
    app.run(port=5555, debug=True)
